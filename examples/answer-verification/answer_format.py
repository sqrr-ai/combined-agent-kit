"""Strict input format for the synthetic business-answer verification exercise.

This module validates data shapes. It does not authenticate supplied evidence.
"""

import datetime as dt
import json
import re
from pathlib import Path

SCHEMA_VERSION = "1.0.0"
MAX_BYTES = 524288
MAX_INTEGER = 9007199254740991  # Exact integer range shared with JavaScript.
MAX_CASES = 64
MAX_ROWS = 256
ID = re.compile(r"[a-z][a-z0-9_-]{0,79}\Z", re.ASCII)
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z", re.ASCII)
TIMEZONE = re.compile(r"(?:UTC|[A-Za-z_]+/[A-Za-z_+-]+)\Z", re.ASCII)


class InputError(ValueError):
    """The input is outside the deliberately small teaching format."""


def require(condition, message):
    if not condition:
        raise InputError(message)


def object_fields(value, fields, path):
    require(type(value) is dict, path + " must be an object")
    require(set(value) == set(fields.split()), path + " has missing or unknown fields")


def text(value, path, maximum=4096):
    require(type(value) is str and 0 < len(value) <= maximum, path + " must be bounded text")
    require(
        not any(0xD800 <= ord(char) <= 0xDFFF for char in value),
        path + " contains a surrogate",
    )


def identifier(value, path):
    text(value, path, 80)
    require(ID.fullmatch(value) is not None, path + " must be an ASCII teaching identifier")


def integer(value, path, maximum=MAX_INTEGER):
    require(
        type(value) is int and 0 <= value <= maximum,
        path + " must be a bounded nonnegative integer",
    )


def enum(value, choices, path):
    require(type(value) is str and value in choices, path + " is not an allowed value")


def array(value, path, maximum=MAX_ROWS):
    require(type(value) is list and len(value) <= maximum, path + " must be a bounded array")


def identifiers(value, path):
    array(value, path)
    for item in value:
        identifier(item, path + "[]")
    require(len(value) == len(set(value)), path + " contains duplicate identifiers")


def timestamp(value, path):
    text(value, path, 20)
    require(
        TIMESTAMP.fullmatch(value) is not None,
        path + " must be a whole-second UTC timestamp ending Z",
    )
    try:
        return dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise InputError(path + " is not a real calendar timestamp") from error


def interval(value, path):
    object_fields(value, "start endExclusive timezone", path)
    start = timestamp(value["start"], path + ".start")
    end = timestamp(value["endExclusive"], path + ".endExclusive")
    require(start < end, path + " must have start before endExclusive")
    text(value["timezone"], path + ".timezone", 80)
    require(
        TIMEZONE.fullmatch(value["timezone"]) is not None,
        path + " has an invalid timezone label",
    )


def currency(value, path):
    text(value, path, 3)
    require(
        re.fullmatch(r"[A-Z]{3}", value, re.ASCII) is not None,
        path + " must use three ASCII capitals",
    )


def validate_contract(value):
    path = "questionContract"
    object_fields(
        value,
        "accountId requiredDatasetIds metric interval currency unit asOf "
        "maxSourceAgeSeconds requireCompletePopulation",
        path,
    )
    identifier(value["accountId"], path + ".accountId")
    identifiers(value["requiredDatasetIds"], path + ".requiredDatasetIds")
    require(bool(value["requiredDatasetIds"]), path + " requires at least one dataset")
    enum(value["metric"], ["paid_invoice_total"], path + ".metric")
    interval(value["interval"], path + ".interval")
    require(
        value["interval"]["timezone"] == "UTC",
        "This format's question contract uses UTC only",
    )
    currency(value["currency"], path + ".currency")
    enum(value["unit"], ["minor"], path + ".unit")
    timestamp(value["asOf"], path + ".asOf")
    integer(value["maxSourceAgeSeconds"], path + ".maxSourceAgeSeconds", 2678400)
    require(
        value["requireCompletePopulation"] is True,
        "This contract requires a complete population answer",
    )


def validate_evidence(value, path):
    object_fields(
        value,
        "accountId datasetIds queryId outcome interval lastSuccessAt coverage truncated rows",
        path,
    )
    identifier(value["accountId"], path + ".accountId")
    identifiers(value["datasetIds"], path + ".datasetIds")
    if value["queryId"] is not None:
        identifier(value["queryId"], path + ".queryId")
    enum(value["outcome"], ["success", "access_denied", "error"], path + ".outcome")
    interval(value["interval"], path + ".interval")
    if value["lastSuccessAt"] is not None:
        timestamp(value["lastSuccessAt"], path + ".lastSuccessAt")
    enum(value["coverage"], ["complete", "partial", "unknown"], path + ".coverage")
    require(
        value["truncated"] is None or type(value["truncated"]) is bool,
        path + ".truncated must be boolean or null",
    )
    array(value["rows"], path + ".rows")
    row_ids = []
    for index, row in enumerate(value["rows"]):
        row_path = path + ".rows[" + str(index) + "]"
        object_fields(row, "id datasetId accountId paidAt status currency unit value", row_path)
        for key in ["id", "datasetId", "accountId"]:
            identifier(row[key], row_path + "." + key)
        timestamp(row["paidAt"], row_path + ".paidAt")
        enum(row["status"], ["paid", "open", "void"], row_path + ".status")
        currency(row["currency"], row_path + ".currency")
        enum(row["unit"], ["minor", "major"], row_path + ".unit")
        integer(row["value"], row_path + ".value")
        row_ids.append(row["id"])
    require(
        len(row_ids) == len(set(row_ids)),
        path + ".rows contains duplicate evidence IDs",
    )
    require(
        sum(row["value"] for row in value["rows"]) <= MAX_INTEGER,
        path + ".rows aggregate exceeds the exact-integer limit",
    )


def validate_claim(value, path):
    object_fields(
        value,
        "accountId metric interval currency unit value population evidenceIds recordClaims",
        path,
    )
    identifier(value["accountId"], path + ".accountId")
    enum(value["metric"], ["paid_invoice_total"], path + ".metric")
    interval(value["interval"], path + ".interval")
    currency(value["currency"], path + ".currency")
    enum(value["unit"], ["minor", "major"], path + ".unit")
    integer(value["value"], path + ".value")
    enum(value["population"], ["complete", "partial"], path + ".population")
    identifiers(value["evidenceIds"], path + ".evidenceIds")
    array(value["recordClaims"], path + ".recordClaims")
    pairs = []
    for index, fact in enumerate(value["recordClaims"]):
        fact_path = path + ".recordClaims[" + str(index) + "]"
        object_fields(fact, "evidenceId field value", fact_path)
        identifier(fact["evidenceId"], fact_path + ".evidenceId")
        enum(fact["field"], ["status", "currency", "accountId"], fact_path + ".field")
        text(fact["value"], fact_path + ".value", 80)
        pairs.append((fact["evidenceId"], fact["field"]))
    require(
        len(pairs) == len(set(pairs)),
        path + ".recordClaims contains duplicate evidence/field pairs",
    )


def validate_bundle(value):
    object_fields(value, "schemaVersion fixtureSetId questionContract cases", "root")
    require(value["schemaVersion"] == SCHEMA_VERSION, "Unsupported schemaVersion")
    identifier(value["fixtureSetId"], "fixtureSetId")
    validate_contract(value["questionContract"])
    array(value["cases"], "cases", MAX_CASES)
    require(bool(value["cases"]), "At least one case is required")
    case_ids = []
    for index, case in enumerate(value["cases"]):
        path = "cases[" + str(index) + "]"
        object_fields(case, "id title question answer evidence claim", path)
        identifier(case["id"], path + ".id")
        for key in ["title", "question", "answer"]:
            text(case[key], path + "." + key)
        validate_evidence(case["evidence"], path + ".evidence")
        validate_claim(case["claim"], path + ".claim")
        case_ids.append(case["id"])
    require(len(case_ids) == len(set(case_ids)), "Duplicate case IDs")
    return value


def _pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "Duplicate JSON object key")
        result[key] = value
    return result


def _no_float(_value):
    raise InputError("Floating-point, exponent and non-finite numbers are not supported")


def _integer(value):
    require(len(value.lstrip("-")) <= 16, "JSON integer is too large")
    return int(value)


def _bounded_depth(value):
    pending = [(value, 0)]
    while pending:
        item, depth = pending.pop()
        require(depth <= 16, "JSON input exceeds the nesting limit")
        if type(item) is dict:
            pending.extend((child, depth + 1) for child in item.values())
        elif type(item) is list:
            pending.extend((child, depth + 1) for child in item)
    return value


def read_json(path):
    """The caller chooses this path; JSON content never supplies file paths."""
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "JSON input exceeds the size limit")
    try:
        return _bounded_depth(
            json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=_pairs,
                parse_float=_no_float,
                parse_constant=_no_float,
                parse_int=_integer,
            )
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise InputError("Input must be bounded valid UTF-8 JSON") from error
