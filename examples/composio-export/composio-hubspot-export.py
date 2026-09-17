#!/usr/bin/env python3
"""Bounded HubSpot contacts export. Offline fixture mode is the default.

Python 3.10+, standard library only. See the companion README for coverage.
Live mode uses Composio Proxy v3.1 and HubSpot's 2026-09 contacts GET endpoint.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROXY_URL = "https://backend.composio.dev/api/v3.1/tools/execute/proxy"
PROVIDER_URL = "https://api.hubapi.com/crm/objects/2026-09/contacts"
PROPERTIES = ("firstname", "lastname", "email", "createdate", "lastmodifieddate")
RETRYABLE = {429, 500, 502, 503, 504}
MAX_RESPONSE_BYTES = 5 * 1024 * 1024


class ExportError(Exception):
    """Static error codes only: never echo credentials or provider payloads."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ExportError("unexpected_http_redirect")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def request_body(account, after, limit):
    if not isinstance(account, str) or not account.strip():
        raise ExportError("connected_account_required")
    query = {"limit": str(limit), "archived": "false", "properties": ",".join(PROPERTIES)}
    if after is not None:
        query["after"] = after
    return {
        "connected_account_id": account,
        "method": "GET",
        "endpoint": PROVIDER_URL + "?" + urllib.parse.urlencode(query),
    }


def live_page(account, key, after, limit, *, opener=None, sleep=time.sleep):
    """At most three attempts, fixed HTTPS destination, no redirect following."""
    if not isinstance(key, str) or not key.strip():
        raise ExportError("project_api_key_required")
    opener = opener or urllib.request.build_opener(NoRedirect()).open
    payload = json.dumps(request_body(account, after, limit)).encode()
    for attempt in range(3):
        req = urllib.request.Request(
            PROXY_URL, data=payload, method="POST",
            headers={"Content-Type": "application/json", "x-api-key": key},
        )
        try:
            with opener(req, timeout=30) as response:
                status = response.status
                raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ExportError("response_size_limit")
            if status != 200:
                raise ExportError("unexpected_outer_status")
            try:
                wrapper = json.loads(raw)
            except (ValueError, UnicodeDecodeError) as exc:
                raise ExportError("invalid_response_json") from exc
            if not isinstance(wrapper, dict) or type(wrapper.get("status")) is not int:
                raise ExportError("invalid_proxy_response")
            upstream = wrapper["status"]
            if upstream in RETRYABLE and attempt < 2:
                sleep(2 ** attempt)
                continue
            if upstream != 200:
                raise ExportError("upstream_status_" + str(upstream))
            return wrapper.get("data")
        except urllib.error.HTTPError as exc:
            exc.close()
            if exc.code in RETRYABLE and attempt < 2:
                sleep(2 ** attempt)
                continue
            raise ExportError("composio_http_" + str(exc.code)) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < 2:
                sleep(2 ** attempt)
                continue
            raise ExportError("transport_failed") from exc
    raise ExportError("retry_limit")


def fixture_reader(path):
    fixture = json.loads(path.read_text(encoding="utf-8"))
    if fixture.get("synthetic") is not True or not isinstance(fixture.get("pages"), list):
        raise ExportError("invalid_synthetic_fixture")
    pages = fixture["pages"]

    def read(after, limit):
        matches = [p for p in pages if p.get("request_after") == after]
        if len(matches) != 1:
            raise ExportError("fixture_cursor_not_unique")
        return matches[0]["data"]

    return read


def validate_page(data, limit):
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ExportError("invalid_contacts_response")
    records = data["results"]
    if len(records) > limit:
        raise ExportError("provider_exceeded_requested_limit")
    for record in records:
        if (not isinstance(record, dict) or not isinstance(record.get("id"), str)
                or not record["id"] or not isinstance(record.get("properties"), dict)):
            raise ExportError("invalid_contact_record")
        if record.get("archived") is True:
            raise ExportError("unexpected_archived_contact")
    paging = data.get("paging", {})
    if not isinstance(paging, dict):
        raise ExportError("invalid_paging")
    if "next" not in paging:
        return records, None
    next_page = paging["next"]
    if not isinstance(next_page, dict):
        raise ExportError("invalid_next_page")
    after = next_page.get("after")
    if not isinstance(after, str) or not after.strip():
        raise ExportError("invalid_next_cursor")
    return records, after


def csv_cell(value):
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    # Protect spreadsheet imports; the original value remains in records.jsonl.
    if text.startswith(("\t", "\r", "\n")) or text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def save_manifest(out, manifest):
    temporary = out / ".manifest.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(out / "manifest.json")


def export_contacts(read_page, out, *, mode="fixture", max_pages=10, max_records=500):
    if not 1 <= max_pages <= 100 or not 1 <= max_records <= 5000:
        raise ExportError("bounds_out_of_range")
    # A new private directory prevents overwriting or mixing two runs.
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    manifest = {
        "mode": mode, "synthetic": mode == "fixture", "started_at": now(),
        "composio_api": "v3.1 proxy", "provider_endpoint": PROVIDER_URL,
        "properties": list(PROPERTIES), "archived": False,
        "max_pages": max_pages, "max_records": max_records,
        "pages": 0, "received_records": 0, "unique_records": 0,
        "duplicate_records": 0, "next_cursor": None, "complete": False,
        "reason": "started", "coverage": "Active contacts, selected current properties only.",
        "csv_policy": "Last observed record per ID; null/missing empty; formula-like text prefixed with apostrophe.",
        "jsonl_policy": "All accepted records, including duplicates, preserved in receipt order.",
    }
    save_manifest(out, manifest)
    latest, seen_cursors = {}, set()
    cursor = None
    exhausted = False
    try:
        with (out / "records.jsonl").open("x", encoding="utf-8") as raw:
            while manifest["pages"] < max_pages and manifest["received_records"] < max_records:
                limit = min(50, max_records - manifest["received_records"])
                records, next_cursor = validate_page(read_page(cursor, limit), limit)
                if next_cursor is not None and next_cursor in seen_cursors:
                    raise ExportError("cursor_cycle")
                for record in records:
                    raw.write(json.dumps(record, ensure_ascii=False) + "\n")
                raw.flush()
                os.fsync(raw.fileno())
                for record in records:
                    latest[record["id"]] = record
                manifest["pages"] += 1
                manifest["received_records"] += len(records)
                manifest["unique_records"] = len(latest)
                manifest["duplicate_records"] = manifest["received_records"] - len(latest)
                manifest["next_cursor"] = next_cursor
                manifest["reason"] = "page_saved"
                save_manifest(out, manifest)
                if next_cursor is None:
                    exhausted = True
                    break
                seen_cursors.add(next_cursor)
                cursor = next_cursor
            manifest["reason"] = "end_of_listing" if exhausted else "configured_limit"
    except ExportError as exc:
        manifest["reason"] = str(exc)
    except (OSError, ValueError, TypeError, KeyError):
        manifest["reason"] = "local_io_or_fixture_error"
    finally:
        columns = ["id", "createdAt", "updatedAt", *PROPERTIES]
        with (out / "contacts.csv").open("x", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=columns)
            writer.writeheader()
            for record in latest.values():
                row = {key: record.get(key) for key in columns[:3]}
                row.update({key: record["properties"].get(key) for key in PROPERTIES})
                writer.writerow({key: csv_cell(value) for key, value in row.items()})
            target.flush()
            os.fsync(target.fileno())
        manifest["complete"] = exhausted and manifest["reason"] == "end_of_listing"
        manifest["finished_at"] = now()
        save_manifest(out, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Use your Composio connection; provider charges may apply.")
    parser.add_argument("--fixture", type=Path, default=Path(__file__).with_name("composio-hubspot-sample.json"))
    parser.add_argument("--out", type=Path, default=Path("hubspot-export-sample"))
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--max-records", type=int, default=500)
    args = parser.parse_args()
    try:
        if args.live:
            key = os.environ.get("COMPOSIO_API_KEY", "")
            account = os.environ.get("HUBSPOT_CONNECTED_ACCOUNT_ID", "")
            if not key or not account:
                raise ExportError("live_mode_requires_key_and_explicit_account")
            read_page = lambda after, limit: live_page(account, key, after, limit)
        else:
            read_page = fixture_reader(args.fixture)
        manifest = export_contacts(read_page, args.out, mode="live" if args.live else "fixture",
                                   max_pages=args.max_pages, max_records=args.max_records)
        print(json.dumps({k: manifest[k] for k in ["mode", "pages", "received_records", "unique_records", "complete", "reason"]}))
        return 0 if manifest["complete"] else 2
    except ExportError as exc:
        print("Export stopped: " + str(exc), file=sys.stderr)
    except FileExistsError:
        print("Output directory exists; choose a new --out path.", file=sys.stderr)
    except (OSError, ValueError, TypeError, KeyError):
        print("Export stopped: local_io_or_fixture_error", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
