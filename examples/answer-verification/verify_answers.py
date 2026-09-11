#!/usr/bin/env python3
"""Check supplied structured answers against a small synthetic evidence contract.

No model, SQL, network, or credentials are used. Human-readable answer text is
illustrative; only the structured claim and supplied evidence are checked.
"""

import argparse
import json
import sys
from pathlib import Path

from answer_format import (
    SCHEMA_VERSION,
    InputError,
    array,
    enum,
    identifier,
    identifiers,
    object_fields,
    read_json,
    require,
    text,
    timestamp,
    validate_bundle,
)


def same_window(left, right):
    return (left["start"], left["endExclusive"]) == (
        right["start"],
        right["endExclusive"],
    )


def evaluate_case(case, contract):
    evidence, claim = case["evidence"], case["claim"]
    checks = []

    def add(code, status, message):
        checks.append({"code": code, "status": status, "message": message})

    def compare(code, condition, good, bad):
        add(code, "pass" if condition else "fail", good if condition else bad)

    account_ok = evidence["accountId"] == contract["accountId"]
    compare(
        "evidence_account",
        account_ok,
        "Evidence names the requested account.",
        "Evidence names a different account; matching numbers cannot establish "
        "the requested account's answer.",
    )
    compare(
        "claim_account",
        claim["accountId"] == contract["accountId"],
        "The claim names the requested account.",
        "The claim names a different account.",
    )
    compare(
        "claim_metric",
        claim["metric"] == contract["metric"],
        "The structured metric matches the question.",
        "The structured metric differs from the question.",
    )
    datasets_ok = set(contract["requiredDatasetIds"]) <= set(evidence["datasetIds"])
    add(
        "required_datasets",
        "pass" if datasets_ok else "insufficient_evidence",
        "The supplied selection includes every required dataset."
        if datasets_ok
        else "A required dataset is absent; missing access or data does not establish a total.",
    )
    evidence_window_ok = same_window(evidence["interval"], contract["interval"])
    compare(
        "evidence_interval",
        evidence_window_ok,
        "Evidence describes the requested half-open interval.",
        "Evidence describes a different interval.",
    )
    evidence_zone_ok = evidence["interval"]["timezone"] == contract["interval"]["timezone"]
    compare(
        "evidence_timezone",
        evidence_zone_ok,
        "Evidence uses the requested timezone label.",
        "Evidence uses a different timezone label.",
    )
    compare(
        "claim_interval",
        same_window(claim["interval"], contract["interval"]),
        "The claim uses the requested interval.",
        "The claim changes the requested reporting interval.",
    )
    compare(
        "claim_timezone",
        claim["interval"]["timezone"] == contract["interval"]["timezone"],
        "The claim uses the requested timezone label.",
        "The claim changes the requested reporting timezone.",
    )
    compare(
        "claim_currency",
        claim["currency"] == contract["currency"],
        "The claim keeps the requested currency.",
        "The claim changes currency without a conversion contract.",
    )
    compare(
        "claim_unit",
        claim["unit"] == contract["unit"],
        "The claim keeps integer minor units.",
        "The claim changes the monetary unit.",
    )
    query_ok = evidence["outcome"] == "success"
    compare(
        "query_outcome",
        query_ok,
        "The supplied query outcome is success.",
        "The query did not succeed; an access error or other failure "
        "is not evidence for zero activity.",
    )
    add(
        "query_reference",
        "pass" if evidence["queryId"] else "insufficient_evidence",
        "A supplied query reference is present; its authenticity is not checked."
        if evidence["queryId"]
        else "No query reference was supplied.",
    )
    if evidence["lastSuccessAt"] is None:
        add(
            "source_freshness",
            "insufficient_evidence",
            "The last successful source commit is unknown.",
        )
    else:
        age = int(
            (
                timestamp(contract["asOf"], "asOf")
                - timestamp(evidence["lastSuccessAt"], "lastSuccessAt")
            ).total_seconds()
        )
        compare(
            "source_freshness",
            0 <= age <= contract["maxSourceAgeSeconds"],
            "The supplied commit time is within the stated freshness window.",
            "The supplied source commit is outside the freshness policy or is in the future.",
        )
    add(
        "evidence_coverage",
        "pass" if evidence["coverage"] == "complete" else "insufficient_evidence",
        "The supplied coverage metadata says complete; "
        "upstream completeness is not independently proved."
        if evidence["coverage"] == "complete"
        else "Supplied coverage is partial or unknown.",
    )
    if evidence["truncated"] is None:
        add(
            "result_truncation",
            "insufficient_evidence",
            "Whether the supplied result was truncated is unknown.",
        )
    elif evidence["truncated"]:
        add(
            "result_truncation",
            "fail" if claim["population"] == "complete" else "insufficient_evidence",
            "A truncated result cannot establish the claimed complete population total.",
        )
    else:
        add("result_truncation", "pass", "The supplied result is marked untruncated.")
    add(
        "population",
        "pass" if claim["population"] == "complete" else "insufficient_evidence",
        "The claim addresses a complete population."
        if claim["population"] == "complete"
        else "The claim is partial but the question requires a complete population answer.",
    )

    rows = evidence["rows"]
    row_scope_ok = all(
        row["accountId"] == evidence["accountId"]
        and row["datasetId"] in evidence["datasetIds"]
        and row["currency"] == contract["currency"]
        and row["unit"] == contract["unit"]
        for row in rows
    )
    compare(
        "row_scope",
        row_scope_ok,
        "Supplied rows are consistent with their declared scope and unit.",
        "A row contradicts the declared account, dataset, currency or unit.",
    )
    by_id = {row["id"]: row for row in rows}
    cited = set(claim["evidenceIds"])
    fact_refs = {fact["evidenceId"] for fact in claim["recordClaims"]}
    citations_ok = (cited | fact_refs) <= set(by_id)
    compare(
        "citation_resolution",
        citations_ok,
        "Every supplied citation resolves inside this evidence object.",
        "At least one citation has no corresponding supplied evidence row.",
    )
    fact_matches = all(
        fact["value"] == by_id[fact["evidenceId"]][fact["field"]]
        for fact in claim["recordClaims"]
        if fact["evidenceId"] in by_id
    )
    if not fact_matches:
        add(
            "record_claims",
            "fail",
            "A structured record claim contradicts its cited field.",
        )
    elif citations_ok:
        compare(
            "record_claims",
            fact_matches,
            "Structured record claims match their cited fields.",
            "A structured record claim contradicts its cited field.",
        )
    else:
        add(
            "record_claims",
            "not_checked",
            "An unresolved citation prevents a complete record-claim check.",
        )

    can_compare = (
        query_ok
        and datasets_ok
        and account_ok
        and row_scope_ok
        and evidence_window_ok
        and evidence_zone_ok
    )
    if can_compare:
        start = timestamp(contract["interval"]["start"], "start")
        end = timestamp(contract["interval"]["endExclusive"], "endExclusive")
        eligible = [
            row
            for row in rows
            if row["status"] == "paid"
            and row["datasetId"] in contract["requiredDatasetIds"]
            and start <= timestamp(row["paidAt"], "paidAt") < end
        ]
        eligible_ids = {row["id"] for row in eligible}
        if citations_ok:
            compare(
                "cited_population",
                cited == eligible_ids,
                "The aggregate cites exactly the qualifying supplied rows.",
                "Aggregate citations omit a qualifying supplied row "
                "or include an out-of-scope row.",
            )
        else:
            add(
                "cited_population",
                "not_checked",
                "An unresolved citation prevents a complete citation-set check.",
            )
        compare(
            "claim_value",
            claim["value"] == sum(row["value"] for row in eligible),
            "The structured amount equals the qualifying supplied row total.",
            "The structured amount differs from the qualifying supplied row total.",
        )
    else:
        add(
            "cited_population",
            "not_checked",
            "Query outcome, dataset or scope evidence is insufficient for a population comparison.",
        )
        add(
            "claim_value",
            "not_checked",
            "No numeric verdict is inferred from a failed query or missing/wrong-scope evidence.",
        )
    reasons = [
        {"code": check["code"], "message": check["message"]}
        for check in checks
        if check["status"] in ["fail", "insufficient_evidence"]
    ]
    statuses = {check["status"] for check in checks}
    judgment = (
        "fail"
        if "fail" in statuses
        else ("insufficient_evidence" if "insufficient_evidence" in statuses else "pass")
    )
    return {
        "id": case["id"],
        "judgment": judgment,
        "checks": checks,
        "reasons": reasons,
    }


def evaluate(bundle):
    validate_bundle(bundle)
    results = [evaluate_case(case, bundle["questionContract"]) for case in bundle["cases"]]
    summary = {"total": len(results)}
    for judgment in ["pass", "fail", "insufficient_evidence"]:
        summary[judgment] = sum(result["judgment"] == judgment for result in results)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "fixtureSetId": bundle["fixtureSetId"],
        "summary": summary,
        "results": results,
    }


def compare_expected(observed, expected):
    object_fields(expected, "schemaVersion fixtureSetId results", "expected")
    require(expected["schemaVersion"] == SCHEMA_VERSION, "Expected schemaVersion differs")
    require(
        expected["fixtureSetId"] == observed["fixtureSetId"],
        "Expected fixtureSetId differs",
    )
    array(expected["results"], "expected.results", 64)
    expected_by_id = {}
    for item in expected["results"]:
        object_fields(item, "id judgment reasonCodes explanation", "expected.result")
        identifier(item["id"], "expected.id")
        require(item["id"] not in expected_by_id, "Duplicate expected case ID")
        enum(
            item["judgment"],
            ["pass", "fail", "insufficient_evidence"],
            "expected.judgment",
        )
        identifiers(item["reasonCodes"], "expected.reasonCodes")
        text(item["explanation"], "expected.explanation")
        expected_by_id[item["id"]] = item
    actual_by_id = {item["id"]: item for item in observed["results"]}
    require(
        set(expected_by_id) == set(actual_by_id),
        "Expected and observed case IDs differ",
    )
    mismatches = []
    for case_id, item in actual_by_id.items():
        reference = expected_by_id[case_id]
        codes = [reason["code"] for reason in item["reasons"]]
        if item["judgment"] != reference["judgment"] or codes != reference["reasonCodes"]:
            mismatches.append(case_id)
    return mismatches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "cases",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().with_name("cases.json"),
    )
    parser.add_argument(
        "--verify",
        type=Path,
        help="Compare judgments and ordered reason codes with an independent expected file",
    )
    arguments = parser.parse_args()
    try:
        observed = evaluate(read_json(arguments.cases))
        mismatches = (
            compare_expected(observed, read_json(arguments.verify)) if arguments.verify else []
        )
        print(json.dumps(observed, indent=2, ensure_ascii=False, allow_nan=False))
        if mismatches:
            print(
                json.dumps({"error": "expected_mismatch", "caseIds": mismatches}),
                file=sys.stderr,
            )
            return 1
        return 0
    except (InputError, OSError) as error:
        print(
            json.dumps({"error": "invalid_input", "message": str(error)}),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
