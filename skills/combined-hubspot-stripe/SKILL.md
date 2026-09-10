---
name: combined-hubspot-stripe
description: Compare HubSpot open pipeline with Stripe paid invoices using Combined's granted datasets, explicit customer mapping, separate aggregation, and currency-aware time windows. Use for CRM and billing analysis without double-counting.
---

# HubSpot pipeline and Stripe payments

Answer questions such as “Which companies have open opportunities, and what have their paid invoices totaled in the last 90 days?” using the HubSpot and Stripe sources already available to the user's Combined agent.

## Establish the calculation

Respect the user's metric and time range. For “last 90 complete UTC days,” use the interval from UTC midnight 90 days before today to today's UTC midnight, with an exclusive upper bound. Use the invoice payment timestamp for paid-invoice collections; invoice creation time answers a different question.

Open pipeline is the unweighted amount of deals whose stage is open. Map closed-won, closed-lost, and custom stages from the actual source data or a user-supplied mapping. Do not infer stage meaning from an unfamiliar identifier.

Paid invoice amount is not automatically MRR, ARR, recognized revenue, or revenue net of refunds. If the user requests one of those metrics, identify the necessary subscription, credit, refund, or accounting records instead of relabeling invoice totals.

## Discover and join

1. Use `list_sources`, `list_datasets`, and `describe_dataset` to find the actual logical relations and fields. Obtain company and deal IDs, company associations, stage, amount and currency; for invoices obtain customer ID, status, amount paid, currency and payment timestamp.
2. Check source freshness with `get_freshness`. A missing successful commit limits the available answer.
3. Find the explicit HubSpot-company to Stripe-customer mapping, such as an existing CRM property, Stripe metadata field, or maintained mapping dataset. Each Stripe customer should resolve to one company for this calculation. One company may own multiple billing customer IDs.
4. Check missing and duplicate mapping keys. Keep unresolved records separate; company names and shared email domains are insufficient to silently merge customers.
5. Aggregate open deals by company and currency. Separately aggregate qualifying paid invoices by mapped company and currency. Join the aggregates and keep companies with open pipeline even when no invoice matches.

Only use `query_sql` for one bounded, read-only `SELECT` or CTE-to-`SELECT` over the granted relations. Bind time bounds and filter values through parameters. Use real catalogue identifiers; the teaching fixture's names are not connector schemas.

## Currency and completeness

Keep currencies separate unless the user provides an explicit conversion method and rate date. Interpret stored units using the source schema and current provider documentation. Dividing by 100 is correct for the included USD/EUR teaching fixture, not every currency.

Compute aggregates over the eligible data before limiting the displayed companies. A null joined invoice total means no matching qualifying row; missing mapping, incomplete ingestion, or currency mismatch can also explain it. Do not call that proven zero collections without resolving coverage.

Return the requested ranking, open-deal count, open-pipeline amount, paid-invoice amount, currency, exact interval, both source timestamps, and the query receipt when supplied. Flag material missing amounts and mappings.

## Reproducible example

The bundled [synthetic DuckDB fixture](assets/hubspot-stripe-pipeline.sql) demonstrates the aggregation pattern without an account or network calls. In its fixed June 12–September 10, 2026 interval, Atlas has USD 20,000 of open pipeline and USD 5,000 on paid invoices. A raw deals-to-invoices join doubles both totals. Birch has USD 6,000 of pipeline and no matching paid invoice; Cedar has EUR 4,000 and EUR 1,500 respectively.

Run the fixture in a local DuckDB environment only when a demonstration or validation is useful. Do not submit its synthetic `VALUES` relations to Combined's production query service. Adapt its aggregate-then-join pattern to the user's discovered, granted datasets.

## References

- [Combined](https://www.trycombined.com/)
- [Worked tutorial](https://www.trycombined.com/resources/query-hubspot-and-stripe-with-ai)
- [MCP tools](https://www.trycombined.com/docs/integrations/mcp)
- [Stripe invoice object](https://docs.stripe.com/api/invoices/object)
- [Stripe currency units](https://docs.stripe.com/currencies#minor-units-in-api-amounts)
