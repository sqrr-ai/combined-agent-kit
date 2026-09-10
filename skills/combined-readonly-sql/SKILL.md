---
name: combined-readonly-sql
description: Write, troubleshoot, and verify bounded read-only DuckDB SQL through Combined's MCP query_sql tool. Use for granted-dataset joins, aggregates, filters, pagination, truncation, or query-policy errors.
---

# Read-only SQL through Combined

Write the smallest query that answers the user's question over the current grant. This skill concerns Combined's MCP query surface, whose output limits are stricter than the general SQL API.

## Resolve the schema

Use `list_sources`, `list_datasets`, and `describe_dataset` when the current logical schema is not already known. A relation has three parts:

```text
"source_alias"."logical_schema"."logical_table"
```

Copy identifiers from trusted catalog metadata and quote them correctly. Provider object names, UI labels, storage paths, and synthetic tutorial table names are not interchangeable with these relations. Values can be bound parameters; identifiers cannot.

## Construct the query

`query_sql` accepts one `SELECT` or common-table-expression sequence ending in `SELECT`. Joins, aggregates, ordering, window functions, and bounded subqueries work within resolved granted relations.

- Bind user-provided filter values with `?` placeholders and a matching `parameters` array. Send timestamps with an explicit timezone offset.
- Select only the required columns and use an explicit `LIMIT` for returned detail.
- Aggregate over eligible data before applying a display limit. Do not calculate totals from a truncated sample.
- Establish the join grain and key. Aggregate independent one-to-many tables before joining when a raw join would multiply measures.
- Preserve `NULL` semantics. Use `IS NULL`; do not automatically turn an unknown amount into zero.

MCP bounds: SQL text up to 16 KiB, up to 100 parameters, `maxRows` default 100 and maximum 1,000. Up to eight sources can be queried. Request, grant, account, result-size, and scan limits can impose lower effective bounds. The typed result may be complete while the human-readable text is only a preview, so inspect `structuredContent`.

The service rejects mutations, multiple statements, system catalogs, file/network reads, unsafe table functions, and extension or database-management statements. Do not work around those constraints by asking for broader credentials or exposing physical storage.

## Handle results and failures

- **Truncated result:** narrow the scope or aggregate. For full detail, use stable `ORDER BY` and keyset predicates, retaining the actual last returned key. SQL results do not have an API cursor. A changing dataset requires a consistent snapshot or an explicit consistency caveat; `OFFSET` is not a repair.
- **Relation or field not found:** refresh metadata and use the current logical names.
- **Policy rejection:** check the single-statement shape, relation grants, limits, and supported functions. Make a specific correction rather than retrying the same query.
- **Timeout:** reduce scan scope, time range, joins, or wide text columns. Preserve any receipt/correlation ID; repeated unchanged retries are not useful.
- **403 or invisible resource:** explain the unavailable scope. A tool being installed does not authorize all account data.

For time-sensitive answers, check source freshness. Return the requested result together with its time bounds, receipt ID if supplied, and any truncation or coverage issue affecting interpretation. Receipts describe execution; they are not copies of the result rows.

## References

- [Combined](https://www.trycombined.com/)
- [SQL catalogue, policy, and pagination](https://www.trycombined.com/docs/concepts/sql)
- [MCP tool reference](https://www.trycombined.com/docs/integrations/mcp)
- [Query troubleshooting](https://www.trycombined.com/docs/troubleshooting/query-and-mcp)
