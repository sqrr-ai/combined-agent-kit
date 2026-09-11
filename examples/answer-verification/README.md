# Verify a structured business-data answer

A right-looking number can still answer the wrong question. This free exercise checks an explicit business answer against its supplied records, account, reporting interval and evidence metadata. It includes twelve synthetic cases, an independently specified expected result, and a small Python runner. No account, model, network connection or package installation is needed.

The exercise checks **structured claims**. The human-readable `answer` in each case is a teaching label; the runner does not read or grade that prose.

## Run the exercise

Download these files into one directory:

- [verify_answers.py](./verify_answers.py)
- [answer_format.py](./answer_format.py)
- [cases.json](./cases.json)
- [expected.json](./expected.json)

Use Python 3.9 or newer:

```sh
python3 verify_answers.py cases.json --verify expected.json > observed.json
```

The runner writes its result to standard output. It reads only the input paths chosen on the command line and imports the adjacent `answer_format.py` module. JSON values never become file paths, URLs to fetch, SQL, executable expressions or instructions. The command above writes `observed.json` through normal shell redirection.

`--verify` compares every case's judgment and ordered reason codes with `expected.json`. Exit `0` means that comparison matched. Exit `1` means an expected judgment differed. Exit `2` means an input/file error. **Exit `0` does not mean every example answer passes:** nine cases are intentionally wrong and two lack enough evidence. Without `--verify`, exit `0` only means the input was valid and the checks ran; inspect the returned judgments.

The published [observed.json](./observed.json) records **1 pass, 9 failures and 2 insufficient-evidence judgments**, matching the prewritten expectations. [run-metadata.json](./run-metadata.json) records the actual execution environment, times and hashes. The implementation was also checked against [47 input and semantic boundary cases](./validation-results.json), including malformed numbers, duplicate IDs, date boundaries, unknown metadata and CLI error behavior. These are local example results, not measurements of a production agent or Combined service.

## The fixed business question

For the fictional `account-acme`, calculate the complete paid-invoice total in USD for August 2026, using UTC dates and a source commit no more than 24 hours old. The interval includes `2026-08-01T00:00:00Z` and excludes `2026-09-01T00:00:00Z`. The teaching clock is fixed at `2026-09-10T12:00:00Z`; it is unrelated to the time you run the script.

Two supplied paid invoices each contain `250000` USD minor units. Their total is `500000`, or USD 5,000. Both payments fall inside the requested interval. The baseline source commit is two hours before the teaching clock. The records and calculation stay the same in most cases; the exercise changes the claimed answer or its evidence envelope. The missing-dataset and denied-query cases deliberately supply no rows.

Paid invoices are the metric defined for this example. They are not monthly recurring revenue, recognized revenue, profit or a complete accounting model. Currency codes are bounded three-letter labels; the runner does not validate ISO membership, foreign exchange, or every currency's decimal conventions.

## Twelve cases

| Case | Expected judgment | What changes |
| --- | --- | --- |
| `complete-answer` | Pass | All supplied evidence meets the local contract |
| `wrong-account` | Fail | The evidence belongs to Contoso while the question asks about Acme |
| `missing-dataset` | Insufficient evidence | The required dataset and its rows are absent |
| `wrong-window` | Fail | The structured claim changes the interval and timezone |
| `altered-number` | Fail | The claim says 550000 while the rows total 500000 |
| `wrong-currency-unit` | Fail | The same digits become EUR major units |
| `stale-source` | Fail | The source commit is 72 hours old against the 24-hour policy |
| `truncated-population` | Fail | A result marked truncated is described as a complete population |
| `access-error-zero` | Fail | An access-denied result becomes a claim of zero payments |
| `missing-citation` | Fail | A cited evidence ID does not exist in the supplied rows |
| `contradictory-citation` | Fail | A structured claim says an invoice is open; its cited row says paid |
| `missing-metadata` | Insufficient evidence | Commit time, coverage and truncation cannot be established |

Known contradictions yield `fail`. If there is no known contradiction but required evidence is absent or unknown, the judgment is `insufficient_evidence`. A `not_checked` check is not a pass; another check explains which prerequisite is missing. For example, the checker does not infer a numeric verdict from a denied query.

## The versioned answer contract

[cases.json](./cases.json) is the single fixture source. Its `schemaVersion` is `1.0.0`; `questionContract` specifies the expected account, required datasets, metric, UTC interval, currency/unit, fixed decision time, maximum source age and requirement for a complete answer. Its `cases` array contains display text, an `evidence` object and a `claim` object for each case.

`evidence` contains the supplied account and dataset selection, query reference and outcome, reporting interval, last successful commit, coverage, truncation and rows. Each row has an envelope-local unique evidence `id`, dataset/account identifiers, paid timestamp, payment status, currency, unit and integer value. These local IDs are not a claim that provider record IDs are globally unique.

`claim` contains the structured total and reporting scope, the claimed population, the row IDs supporting its aggregate, and optional record-level claims. A record claim compares only an explicitly allowed field (`status`, `currency` or `accountId`) with the referenced row. A valid aggregate cites exactly the qualifying supplied rows: paid invoices in the requested dataset and half-open UTC interval. Open invoices and rows outside the interval do not count. Evidence row order does not affect the result.

The checker compares supplied metadata; it does not implement timezone conversion. This format requires a UTC question contract and UTC timestamps. A different claimed timezone is a mismatch, rather than an invitation to reinterpret the timestamps. Unknown metadata uses the explicit `null` or `unknown` value shown in the fixture; omitting a required structural key is invalid input.

Inputs are limited to 512 KiB, 64 cases, 256 rows/references per case and sixteen levels of JSON nesting. Money uses nonnegative integers in JavaScript's exact integer range, including the sum of supplied rows. Floats, exponent notation, non-finite numbers, booleans used as amounts, duplicate JSON keys, duplicate case/row/reference IDs, duplicate record-field claims, invalid calendar dates and unknown object fields are rejected. The limits keep the downloadable example small and deterministic.

Keep the expected question contract under the evaluator's control. If an agent can rewrite the requested account, interval or evidence, a passing comparison cannot establish that it answered the original question.

## Map this teaching format to a Combined workflow

This envelope is **not Combined's native query response or receipt schema**. The following mapping was reviewed against the product source at revision `8970518506ea6cc22e368fb02e0f81e15d83e2fc`, without calling an account. Inspect the actual returned types before adapting it. [Combined MCP reference](https://www.trycombined.com/docs/integrations/mcp).

| Teaching input | Where a real workflow obtains it |
| --- | --- |
| Expected account | The user's chosen account and authenticated account-scoped MCP URL; do not infer it from the answer text |
| Required dataset IDs and row fields | `list_datasets` and `describe_dataset`, followed by the evaluator's explicit selection and field mapping |
| Returned records | Successful `query_sql` output at `structuredContent.data.rows`, interpreted using `columns`; the human-readable MCP preview may be shortened independently |
| Query reference and row cap | `structuredContent.data.receiptId`, `rowCount` and `truncated` |
| Execution failure | MCP `isError` and its error details, preserving the actual outcome; do not turn an error payload into an empty successful result |
| Last successful commit | `get_freshness` provides source `lastSuccessAt` and selected dataset `lastSuccessAt`; retain the relevant dataset facts instead of substituting a healthy unrelated source |
| Evidence account and dataset selection | Authenticated request context plus the separately retrieved query receipt when available; these are not additional invented fields on `query_sql`'s row result |
| Metric, interval, timezone and units | The agreed question and inspected query/parameters; these definitions must not be invented after seeing the result |
| Complete coverage | A separate review of source selection, required history, filters and query limits; neither a receipt ID nor `truncated: false` establishes it alone |

The native API has a separate `GET /v1/query-receipts/{id}?accountId=...` receipt lookup; there is no `get_receipt` MCP tool in this inspected interface. Receipts expose execution context such as `accountId`, `sourceIds`, `datasetIds` and `state`. Receipt access remains authenticated. [Query receipt API](https://www.trycombined.com/docs/api-reference/endpoints/query/getQueryReceipt), [query troubleshooting](https://www.trycombined.com/docs/troubleshooting/query-and-mcp).

For example, a successful SQL query containing a deliberate `LIMIT` can return `truncated: false` while still representing only a subset of the business population. Check the query and coverage contract separately. Row provenance can help retain the underlying source identity; it does not certify the final interpretation. [Ingestion and provenance](https://www.trycombined.com/docs/concepts/ingestion-and-provenance), [sources and freshness](https://www.trycombined.com/docs/concepts/sources-and-freshness).

## What a pass establishes

A pass means the **supplied structured claim and evidence satisfy this local teaching contract**. It does not authenticate the export, contact the original provider, enforce live tenant grants, prove upstream completeness, check all generated prose, or prove causation. A local string comparison of account labels is not an authorization test. Synthetic IDs and query references are explicitly examples.

To apply the pattern to a real agent, retain the agreed question, original authorized tool response and final structured claims, then adapt the mapping to the discovered schema. Keep evidence outside the agent's ability to silently rewrite it. Separately inspect prose for claims absent from the structured output. [Ragas](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) and [TruLens](https://www.trulens.org/getting_started/core_concepts/rag_triad/) describe broader groundedness evaluation; this small deterministic exercise does not replace them. [Ragas SQL metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/sql/) likewise distinguish executed-result comparison from other evaluation methods.

[Explore Combined](https://www.trycombined.com/) to connect business sources and bring the same evidence checks into your own agent workflow. Start with the [Claude Code setup guide](https://www.trycombined.com/resources/connect-claude-code-to-business-data), [free agent skills](https://www.trycombined.com/agent-skills), or the [browser version of this lab](https://www.trycombined.com/resources/verify-ai-agent-business-data-answers).
