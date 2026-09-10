---
name: combined-revenue-analysis
description: Analyze billing and CRM metrics from Combined while separating pipeline, invoice collections, recurring revenue, and missing data. Use when a revenue question needs explicit definitions, source reconciliation, and checkable SQL.
---

# Revenue analysis with explicit definitions

Produce the business metric the user requested from their granted Combined data. First use the metric definition already supplied by the user or their maintained reporting policy. If “revenue” is ambiguous and the choice changes the answer, resolve whether they mean pipeline, invoice collections, recurring run rate, or accounting revenue before presenting a single total.

## Match the metric to evidence

| Requested metric | Evidence to establish |
|---|---|
| Open pipeline | Deals, amounts, currencies, and the actual mapping of open versus closed stages |
| Paid-invoice collections | Invoice status, amount paid, currency/unit, and payment timestamp |
| Net collections | The chosen cash-collection basis plus attributable refunds or credits under the user's definition |
| MRR or ARR | Subscription and pricing records, billing interval, quantity, currency, effective dates, and the user's treatment of trials, discounts, usage, cancellations, and delinquency |
| Recognized revenue | The organization's accounting recognition source or explicit policy; invoice status alone is insufficient |

Use these as evidence requirements, not invented provider field names. Discover what the workspace actually contains before selecting a formula. When the necessary data is unavailable, give the supported metric with its correct name and explain what is missing for the requested one.

## Work through Combined

Use `list_sources` and `list_datasets` to choose the granted CRM/billing sources; use `describe_dataset` to inspect keys, amount units, currencies, statuses, timestamps, and available history. Check `get_freshness` for relevant source IDs and use the last successful commit as the snapshot time.

Build a read-only aggregate with `query_sql` over the actual logical relations. Use one `SELECT` or CTE-to-`SELECT`, bind filter values with `?` parameters, and return only the necessary fields. The MCP maximum is 1,000 output rows, with lower grant limits possible.

Preserve the intended grain: invoice, subscription, customer, company, or period. If combining several one-to-many relations, aggregate each to the join grain first. Prove the customer-ID mapping before joining CRM and billing. Compare pre-join and post-join row counts or aggregates when join multiplication is plausible.

## Make comparisons meaningful

- Use explicit start/end instants and timezone. Prefer an exclusive upper time bound. Current partial periods and complete prior periods are not directly comparable without qualification.
- Use the event timestamp relevant to the metric. A payment in this month on an older invoice belongs to this month's payment measure.
- Keep currency groups separate. Convert minor units according to currency, not a blanket division by 100.
- Separate a true measured zero from a missing field, absent mapping, missing dataset, or no successful sync.
- Do not reconstruct historical stage movement or historical MRR from a present-day snapshot unless the required history exists.
- Apply display limits after aggregation. Do not extrapolate an account total from the first 100 records.

## Deliver

Return the metric and definition, amount and currency, reporting window, comparison basis, source freshness, and receipt ID when available. Include only the caveats that affect interpretation. If an equivalent provider report is available within the user's authorized scope, reconcile it using the same filters; otherwise retain the reproducible SQL and the unresolved difference.

## References

- [Combined](https://www.trycombined.com/)
- [SQL catalogue and limits](https://www.trycombined.com/docs/concepts/sql)
- [MCP tools](https://www.trycombined.com/docs/integrations/mcp)
- [HubSpot pipeline example](https://www.trycombined.com/resources/connect-hubspot-to-ai-agents)
- [HubSpot and Stripe calculation](https://www.trycombined.com/resources/query-hubspot-and-stripe-with-ai)

Consult the current provider documentation for the selected dataset when its field or currency semantics are uncertain.
