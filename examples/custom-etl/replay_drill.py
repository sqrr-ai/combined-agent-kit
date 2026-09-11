#!/usr/bin/env python3
"""A local synthetic ingestion contract; Python 3.9+, standard library only.

Run: python3 replay_drill.py [--verify expected.json]
Each run creates and removes its own SQLite database beside this script.
This is not a connector, MCP server, or test of any vendor's service.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


PRIMARY = ("billing", "production-us", "invoice")
ACCOUNT = ("billing", "sandbox", "invoice")
ENTITY = ("billing", "production-us", "refund")
SOURCE = ("other-billing", "production-us", "invoice")
EXIT_INTERRUPTED = 73
SCOPE_FIELDS = ("source", "account", "entity")


class ContractError(ValueError):
    pass


def check(actual, expected):
    if actual != expected:
        raise AssertionError(f"Expected {expected!r}; got {actual!r}")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def connect(path):
    db = sqlite3.connect(path, isolation_level=None)
    check(db.execute("PRAGMA journal_mode=DELETE").fetchone()[0], "delete")
    db.execute("PRAGMA synchronous=FULL")
    check(db.execute("PRAGMA synchronous").fetchone()[0], 2)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS records (
          source TEXT, account TEXT, entity TEXT, record_key TEXT,
          revision INTEGER NOT NULL, document TEXT NOT NULL,
          PRIMARY KEY (source, account, entity, record_key));
        CREATE TABLE IF NOT EXISTS revisions (
          source TEXT, account TEXT, entity TEXT, record_key TEXT,
          revision INTEGER, document TEXT NOT NULL,
          PRIMARY KEY (source, account, entity, record_key, revision));
        CREATE TABLE IF NOT EXISTS checkpoints (
          source TEXT, account TEXT, entity TEXT, cursor INTEGER NOT NULL,
          PRIMARY KEY (source, account, entity));
        CREATE TABLE IF NOT EXISTS deliveries (
          source TEXT, account TEXT, entity TEXT, batch_id TEXT,
          digest TEXT NOT NULL, PRIMARY KEY (source, account, entity, batch_id));
    """)
    return db


def checkpoint(db, scope):
    row = db.execute(
        "SELECT cursor FROM checkpoints WHERE source=? AND account=? AND entity=?", scope
    ).fetchone()
    return row[0] if row else 0


def validate(batch):
    scope = tuple(batch.get(field) for field in SCOPE_FIELDS)
    if any(not isinstance(value, str) or not value for value in scope):
        raise ContractError("invalid scope")
    if not isinstance(batch.get("batch_id"), str) or not batch["batch_id"]:
        raise ContractError("invalid batch identity")
    start, end = batch.get("start"), batch.get("end")
    if any(type(value) is not int or value < 0 for value in (start, end)):
        raise ContractError("invalid checkpoint")
    items = batch.get("records")
    if not isinstance(items, list) or not items or end - start != len(items):
        raise ContractError("incomplete feed interval")
    for offset, item in enumerate(items, start + 1):
        if tuple(item.get(field) for field in SCOPE_FIELDS) != scope:
            raise ContractError("record scope differs from batch")
        if type(item.get("position")) is not int or item["position"] != offset:
            raise ContractError("feed positions must be contiguous and ordered")
        if not isinstance(item.get("key"), str) or not item["key"]:
            raise ContractError("invalid record key")
        revision = item.get("revision")
        if type(revision) is not int or not 0 < revision < 2**63:
            raise ContractError("invalid revision")
        document = item.get("document")
        if not isinstance(document, dict) or document.get("op") not in ("upsert", "delete"):
            raise ContractError("invalid operation")
        if document["op"] == "upsert":
            amount = document.get("amount_minor")
            currency = document.get("currency")
            if type(amount) is not int or not 0 <= amount < 2**63:
                raise ContractError("amount must be nonnegative integer minor units")
            if not isinstance(currency, str) or len(currency) != 3 or not (
                currency.isascii() and currency.isalpha() and currency.isupper()
            ):
                raise ContractError("invalid currency label")
    return scope


def apply_batch(db, batch, crash_at=None):
    """All rows, revision evidence, receipt and cursor commit in one database."""
    scope = validate(batch)
    digest = hashlib.sha256(canonical(batch).encode()).hexdigest()
    db.execute("BEGIN IMMEDIATE")
    try:
        receipt = db.execute(
            "SELECT digest FROM deliveries WHERE source=? AND account=? AND entity=? AND batch_id=?",
            (*scope, batch["batch_id"]),
        ).fetchone()
        if receipt:
            if receipt[0] != digest:
                raise ContractError("batch identity reused with different content")
            db.execute("COMMIT")
            return "replayed"
        if checkpoint(db, scope) != batch["start"]:
            raise ContractError("checkpoint does not match committed cursor")
        for index, item in enumerate(batch["records"]):
            key = (*scope, item["key"])
            revision, document = item["revision"], canonical(item["document"])
            seen = db.execute(
                "SELECT document FROM revisions WHERE source=? AND account=? AND entity=? AND record_key=? AND revision=?",
                (*key, revision),
            ).fetchone()
            if seen and seen[0] != document:
                raise ContractError("same revision has conflicting content")
            if not seen:
                db.execute("INSERT INTO revisions VALUES (?,?,?,?,?,?)", (*key, revision, document))
                current = db.execute(
                    "SELECT revision FROM records WHERE source=? AND account=? AND entity=? AND record_key=?", key
                ).fetchone()
                if current is None or revision > current[0]:
                    db.execute("""
                        INSERT INTO records VALUES (?,?,?,?,?,?)
                        ON CONFLICT(source,account,entity,record_key)
                        DO UPDATE SET revision=excluded.revision, document=excluded.document
                    """, (*key, revision, document))
            if crash_at == "mid_batch" and index == 0:
                os._exit(EXIT_INTERRUPTED)
        db.execute("""
            INSERT INTO checkpoints VALUES (?,?,?,?)
            ON CONFLICT(source,account,entity) DO UPDATE SET cursor=excluded.cursor
        """, (*scope, batch["end"]))
        if crash_at == "after_checkpoint":
            os._exit(EXIT_INTERRUPTED)
        db.execute("INSERT INTO deliveries VALUES (?,?,?,?,?)", (*scope, batch["batch_id"], digest))
        db.execute("COMMIT")
        if crash_at == "after_commit":
            os._exit(EXIT_INTERRUPTED)
        return "committed"
    except BaseException:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise


def record(position, key, revision, amount=None, scope=PRIMARY, currency="USD"):
    document = {"op": "delete"} if amount is None else {
        "op": "upsert", "amount_minor": amount, "currency": currency, "business_date": "2026-07-01"
    }
    return dict(zip(SCOPE_FIELDS, scope), position=position, key=key, revision=revision, document=document)


def batch(name, start, *records, scope=PRIMARY):
    return dict(zip(SCOPE_FIELDS, scope), batch_id=name, start=start, end=start + len(records), records=list(records))


def recovery_batch():
    return batch("recovery", 8, record(9, "i3", 1, 5000), record(10, "i1", 5, 18000))


def lost_ack_batch():
    return batch("lost-ack", 10, record(11, "i3", 2, 7000))


def database_state(db):
    # Capture every table, including history/receipts, for rollback assertions.
    return {table: db.execute(f"SELECT * FROM {table} ORDER BY 1,2,3,4,5").fetchall()
            for table in ("records", "revisions", "deliveries")} | {
        "checkpoints": db.execute("SELECT * FROM checkpoints ORDER BY 1,2,3").fetchall()
    }


def summary(db, scope):
    totals, live, tombstones = {}, 0, 0
    for (text,) in db.execute("SELECT document FROM records WHERE source=? AND account=? AND entity=?", scope):
        document = json.loads(text)
        if document["op"] == "delete":
            tombstones += 1
        else:
            live += 1
            currency = document["currency"]
            totals[currency] = totals.get(currency, 0) + document["amount_minor"]
    return [checkpoint(db, scope), dict(sorted(totals.items())), live, tombstones]


def run_drill(directory):
    path = Path(directory) / "synthetic.sqlite"
    db, rows = connect(path), []

    def observe(name, outcome, expected, scope=PRIMARY):
        state = summary(db, scope)
        check(state, expected)
        rows.append([name, outcome, "/".join(scope), *state])

    def commit(name, value, expected, scope=PRIMARY):
        observe(name, apply_batch(db, value), expected, scope)

    def reject(name, value, message):
        before = database_state(db)
        try:
            apply_batch(db, value)
        except ContractError as error:
            check(str(error), message)
        else:
            raise AssertionError(f"{name} was not rejected")
        check(database_state(db), before)
        rows.append([name, "rejected", "/".join(PRIMARY), *summary(db, PRIMARY)])

    def interrupt(name, fault, expected, unchanged):
        nonlocal db
        before = database_state(db)
        db.close()
        child = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--child-db", str(path), "--crash-at", fault],
            capture_output=True, text=True, timeout=15,
        )
        check(child.returncode, EXIT_INTERRUPTED)
        db = connect(path)
        if unchanged:
            check(database_state(db), before)
        observe(name, "process-interrupted", expected)

    initial = batch("initial", 0, record(1, "i1", 1, 10000), record(2, "i2", 1, 20000))
    commit("initial", initial, [2, {"USD": 30000}, 2, 0])
    commit("same-delivery-retry", initial, [2, {"USD": 30000}, 2, 0])
    commit("duplicate-record", batch("duplicate", 2, record(3, "i1", 1, 10000)), [3, {"USD": 30000}, 2, 0])
    commit("newer-update", batch("update", 3, record(4, "i1", 2, 15000)), [4, {"USD": 35000}, 2, 0])
    commit("tombstone", batch("delete", 4, record(5, "i2", 3)), [5, {"USD": 15000}, 1, 1])
    commit("late-business-date-update", batch("late", 5, record(6, "i1", 4, 17500)), [6, {"USD": 17500}, 1, 1])
    commit("unseen-stale-revision", batch("stale", 6, record(7, "i1", 3, 16000)), [7, {"USD": 17500}, 1, 1])
    commit("stale-cannot-resurrect", batch("stale-delete", 7, record(8, "i2", 2, 20000)), [8, {"USD": 17500}, 1, 1])
    reject("conflict-rolls-back-earlier-row", batch("conflict", 8, record(9, "i3", 1, 5000), record(10, "i1", 4, 99900)),
           "same revision has conflicting content")
    reject("historical-revision-conflict", batch("old-conflict", 8, record(9, "i1", 2, 99900)),
           "same revision has conflicting content")
    interrupt("mid-batch-crash", "mid_batch", [8, {"USD": 17500}, 1, 1], True)
    interrupt("checkpoint-before-commit-crash", "after_checkpoint", [8, {"USD": 17500}, 1, 1], True)
    commit("recover-interrupted-batch", recovery_batch(), [10, {"USD": 23000}, 2, 1])
    interrupt("commit-before-ack-crash", "after_commit", [11, {"USD": 25000}, 2, 1], False)
    commit("recover-lost-ack", lost_ack_batch(), [11, {"USD": 25000}, 2, 1])
    commit("separate-account-same-key", batch("initial", 0, record(1, "i1", 99, 90000, ACCOUNT), scope=ACCOUNT),
           [1, {"USD": 90000}, 1, 0], ACCOUNT)
    commit("separate-entity-same-key", batch("initial", 0, record(1, "i1", 1, 1200, ENTITY), scope=ENTITY),
           [1, {"USD": 1200}, 1, 0], ENTITY)
    commit("separate-source-same-key", batch("initial", 0, record(1, "i1", 1, 500, SOURCE), scope=SOURCE),
           [1, {"USD": 500}, 1, 0], SOURCE)
    commit("currencies-stay-separate", batch("eur", 11, record(12, "i4", 1, 5000, currency="EUR")),
           [12, {"EUR": 5000, "USD": 25000}, 3, 1])
    reject("wrong-account-record", batch("wrong-account", 12, record(13, "i5", 1, 100, ACCOUNT)),
           "record scope differs from batch")
    reject("stale-checkpoint", batch("stale-cursor", 11, record(12, "i5", 1, 100)),
           "checkpoint does not match committed cursor")
    reject("future-checkpoint", batch("future-cursor", 13, record(14, "i5", 1, 100)),
           "checkpoint does not match committed cursor")
    incomplete = batch("incomplete", 12, record(13, "i5", 1, 100))
    incomplete["end"] = 14
    reject("missing-feed-position", incomplete, "incomplete feed interval")
    reject("unordered-feed", batch("unordered", 12, record(14, "i5", 1, 100), record(13, "i6", 1, 200)),
           "feed positions must be contiguous and ordered")
    reject("boolean-is-not-revision", batch("bool", 12, record(13, "i5", True, 100)), "invalid revision")
    reject("float-is-not-money", batch("float", 12, record(13, "i5", 1, 1.99)),
           "amount must be nonnegative integer minor units")
    reject("invalid-currency-label", batch("currency", 12, record(13, "i5", 1, 100, currency="U1D")),
           "invalid currency label")
    changed_retry = batch("initial", 0, record(1, "i1", 1, 99900), record(2, "i2", 1, 20000))
    reject("changed-delivery-retry", changed_retry, "batch identity reused with different content")
    commit("old-delivery-retry-after-progress", initial, [12, {"EUR": 5000, "USD": 25000}, 3, 1])
    check(summary(db, ACCOUNT), [1, {"USD": 90000}, 1, 0])
    check(summary(db, ENTITY), [1, {"USD": 1200}, 1, 0])
    check(summary(db, SOURCE), [1, {"USD": 500}, 1, 0])
    db.close()
    return {"synthetic": True, "columns": ["case", "outcome", "scope", "checkpoint", "totals_minor", "live_records", "tombstones"],
            "rows": rows, "passed_cases": len(rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path, help="Compare the complete deterministic output with a saved contract")
    parser.add_argument("--child-db", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--crash-at", choices=("mid_batch", "after_checkpoint", "after_commit"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child_db or args.crash_at:
        if not (args.child_db and args.crash_at):
            parser.error("internal crash arguments must be paired")
        db = connect(args.child_db)
        apply_batch(db, lost_ack_batch() if args.crash_at == "after_commit" else recovery_batch(), args.crash_at)
        raise AssertionError("injected crash did not occur")
    with tempfile.TemporaryDirectory(prefix=".run-", dir=Path(__file__).resolve().parent) as directory:
        result = run_drill(directory)
    if args.verify:
        check(result, json.loads(args.verify.read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
