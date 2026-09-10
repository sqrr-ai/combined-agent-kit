---
name: combined-business-data
description: Answer a business question across sources already connected to Combined by discovering granted datasets, choosing SQL or text retrieval, and reporting source freshness and coverage. Use for cross-app analysis in a Combined workspace.
---

# Business data with Combined

Turn the user's business question into a bounded analysis over their existing Combined sources. Preserve their chosen apps, account, time window, and output. If they supplied files for a one-off analysis, use those files; this skill does not require moving them into Combined.

## Discover the data needed

Use the connected Combined MCP server. Its six read-only tools are `list_sources`, `list_datasets`, `describe_dataset`, `get_freshness`, `search_context`, and `query_sql`. Read the actual tool schemas exposed by the client before calling them; client prefixes may differ.

1. Identify the requested account and sources with `list_sources`. Follow returned cursors when needed; the first page is not necessarily the entire source list.
2. Use `list_datasets` for relevant sources and `describe_dataset` for the required fields. Reuse current schema information already available in the conversation. Build logical relation names from returned metadata, not from provider labels or a tutorial's table names.
3. For time-sensitive questions, use `get_freshness` on the relevant source IDs. It accepts up to eight sources per call. `lastSuccessAt` records a successful commit; authorization completion or a running sync does not establish that records are current.

If a needed source or field is absent, explain what part of the question can still be answered. Use the existing Set up or Access workflow when connection work is requested. The MCP analysis tools do not create connectors, grant access, or send authorization requests.

## Choose the retrieval method

- Use `search_context` for literal phrases across eligible text fields. Its result includes coverage; it is not a semantic or vector search.
- Use `query_sql` for totals, exact filters, comparisons, joins, dates, and selected fields. Aggregate in the query rather than summing a limited sample of rows.
- For cross-source joins, establish an explicit shared identifier or maintained mapping. Company names alone do not establish that records belong to the same customer.
- When both sides contain several records per customer, aggregate to the intended grain before joining. Keep currencies and metric definitions separate.

Submit one bounded, read-only `SELECT` or CTE-to-`SELECT` over granted logical relations. Bind user-provided values with `?` parameters. MCP output defaults to 100 rows and cannot exceed 1,000; account and grant limits may be lower.

## Return the answer

Lead with the business result. Include the metric definition, actual date bounds, relevant source timestamps, and receipt ID when returned. Distinguish complete aggregates from truncated detail. Keep missing mappings, unavailable fields, and incomplete search coverage visible where they affect the conclusion. Do not convert missing records into proven zero activity.

When the question cannot be answered from the available snapshot, state the missing evidence and offer the next useful read or setup action. Do not widen grants or mutate provider records to make the analysis succeed.

## References

- [Combined](https://www.trycombined.com/)
- [MCP tools and limits](https://www.trycombined.com/docs/integrations/mcp)
- [SQL catalogue and policy](https://www.trycombined.com/docs/concepts/sql)
- [Sources and freshness](https://www.trycombined.com/docs/concepts/sources-and-freshness)

Use the maintained references when the live server differs from these instructions.
