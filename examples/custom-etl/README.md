# A replay and recovery drill for an agent data pipeline

This small Python + SQLite exercise shows whether repeated, changed, deleted or interrupted input preserves a defined answer. All records are synthetic. It uses only Python's standard library, local temporary files and child processes; no credentials, network requests or existing database are needed.

Run with Python 3.9+ and its SQLite module (SQLite 3.24+):

```sh
python3 replay_drill.py
```

The script is self-contained. To compare its complete output with the supplied deterministic contract:

```sh
python3 replay_drill.py --verify expected.json > observed.json
```

Exit code zero means all assertions and the optional expected-output comparison passed. The script creates a fresh `.run-*` directory beside itself and removes it afterward. Keep the script in a writable directory. The hidden child-process arguments are internal to the crash drill.

## The data contract

- **Identity:** `(source, provider account, entity, record key)`. The same `i1` key in a different account, source or entity represents a separate record. These names express data identity, not authenticated permissions.
- **Revision:** the synthetic source supplies a monotone per-record revision order using positive integers; feed delivery can still arrive out of order. A newer revision replaces the current record. An unseen older revision is recorded as evidence but cannot replace it. The same revision with identical content is a duplicate; different content is a conflict, even for a historical revision. Real providers do not universally offer this revision contract.
- **Deletion:** a higher-revision tombstone remains stored. An older update cannot resurrect it. The drill retains every seen revision and delivery receipt for clarity; a real service needs a retention policy compatible with its replay window.
- **Checkpoint:** the last committed position in one source/account/entity feed. This exercise deliberately assumes contiguous integer feed positions and rejects missing or reordered positions. Provider revisions, feed positions and the record's business date are different concepts. Actual REST APIs may use opaque cursors and different change guarantees.
- **Money:** nonnegative integer minor units, totaled separately by currency. Labels must be three ASCII uppercase letters; the script does not validate ISO membership or currency-specific decimal rules. USD `25000` means $250; EUR `5000` means €50. This is a current-record arithmetic exercise, not a complete invoice, accounting or revenue model.
- **Transaction:** current records, historical revision evidence, the delivery digest and checkpoint are written in one SQLite transaction. The digest detects a reused delivery ID with changed content. A receipt is checked before the current checkpoint, so a retry can still succeed after later batches have committed.

The late-update case supplies a new revision for a record dated July 1 at a later feed position. It demonstrates applying that supplied update; it does not demonstrate that a real extractor will discover every late upstream change.

## Observed results

The final script passed **29 cases** on Python **3.14.6**, SQLite **3.53.4**. It verifies rollback journaling and `synchronous=FULL` before running. The full output is in [observed.json](./observed.json); the independently specified contract is [expected.json](./expected.json). [run-metadata.json](./run-metadata.json) records the execution environment and artifact hashes.

| Stage | Observed primary invoice result |
| --- | --- |
| Initial two records, then delivery retry and duplicate record | $300; retries do not add money |
| Newer update, then tombstone | $350, then $150 |
| Late update, older update, attempted stale resurrection | $175 throughout the two stale cases |
| Conflict after a valid earlier row | Entire batch rolls back; $175 and checkpoint 8 remain |
| Process exits mid-batch or after checkpoint update, before commit | All four tables match their previous committed state |
| Recovery | $230 and checkpoint 10 |
| Process exits after commit but before acknowledgment; delivery retried | $250 and checkpoint 11; retry reports `replayed` |
| Additional EUR record | $250 and €50 remain separate; checkpoint 12 |

Three fault cases run in separate processes and call `os._exit(73)`, so they bypass Python exception handlers and normal connection cleanup. The parent checks the exit code and reopens the database. Other negative cases reject mixed-account records, stale/future checkpoints, missing/reordered feed positions, a boolean revision, floating-point money, an invalid currency label, historical revision conflicts and changed delivery replays. Every rejection compares all four database tables before and after. Separate source/account/entity cases verify that identical record and delivery IDs do not collide.

## What the results establish

This synthetic drill passed 29 local cases, including transaction rollback across abrupt process exits and retry after a lost acknowledgment. The files above let you inspect and reproduce those results.

It does **not** test Combined, dlt or another vendor's service. It does not implement a source connector, prove upstream completeness, authenticate tenants, enforce agent grants, run an MCP server, test concurrent writers or establish distributed exactly-once delivery. The process exits are not power-loss, disk-fault or cloud-failover experiments. All state in this example shares one database; coordinating an external provider checkpoint and a separate destination requires its own design.

## Primary research behind the design

SQLite documents explicit transaction boundaries and `BEGIN IMMEDIATE` writer acquisition. Its rollback-journal design explains why incomplete local transactions can be recovered; its hardware/filesystem assumptions still matter. The Python module provides the interface used here. [SQLite transactions](https://www.sqlite.org/lang_transaction.html), [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html), [Python sqlite3](https://docs.python.org/3/library/sqlite3.html).

Existing ingestion libraries already provide useful primitives. dlt documents cursor tracking, duplicate handling, merge keys, revision ordering hints and explicit delete handling. This drill illustrates a contract independently; it neither imports dlt nor measures it. [dlt cursor loading](https://dlthub.com/docs/general-usage/incremental/cursor), [dlt merge loading](https://dlthub.com/docs/general-usage/merge-loading).

Pair this exercise with the [platform evaluation worksheet](https://www.trycombined.com/examples/business-data-platform-evaluation.md) and [Salesforce–Stripe workflow](https://www.trycombined.com/resources/opportunities-and-paid-invoices) to evaluate one useful business answer. Combined's [ingestion and provenance](https://www.trycombined.com/docs/concepts/ingestion-and-provenance) describes its own commit/checkpoint model; a documentation comparison must remain distinct from this local execution evidence.
