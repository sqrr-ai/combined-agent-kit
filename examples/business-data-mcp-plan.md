# Business-data MCP plan

Which useful analyses can I run across these business apps?

Reference date: 2026-09-10. This is a planning reference; no account connection or customer-data query has been performed.

## Selected apps

- HubSpot — Supplies a matched analysis. Guide: https://www.trycombined.com/connectors/hubspot. Upstream reference: https://docs.airbyte.com/integrations/sources/hubspot. Reference dataset hints: contacts, companies, deals, campaigns, companies_property_history, contact_lists.
- Stripe — Supplies a matched analysis. Guide: https://www.trycombined.com/connectors/stripe. Upstream reference: https://docs.airbyte.com/integrations/sources/stripe. Reference dataset hints: customers, invoices, charges, subscriptions, refunds, events.
- Intercom — Supplies a matched analysis. Guide: https://www.trycombined.com/connectors/intercom. Upstream reference: https://docs.airbyte.com/integrations/sources/intercom. Reference dataset hints: conversations, contacts, conversation_parts, teams, companies, activity_logs.

## Setup and coverage

1. In Combined Connected Apps, check each source's current Ready status and setup form. Authorize there, choose datasets and complete the first successful sync.
2. Grant the agent these sources explicitly in Access or Set up. A new source does not automatically enter an ordinary grant.
3. Discover the actual source and dataset schemas. The public catalog lists reference names, not guaranteed live tables or complete field lists.
4. Validate each identity map, duplicate keys and unmatched records. Give every calculation a clear reporting unit before combining results.
5. Check successful commits, available date coverage and the freshness needed for the decision. Missing coverage is unknown, not zero.
6. Agree date boundaries, states, measure definitions and currency units. Compute on all eligible records, then display a bounded answer with supporting evidence.

## Matched worked examples

### HubSpot pipeline and Stripe paid invoices

Reporting unit: One row per CRM company and currency.

Map each scoped Stripe customer to its HubSpot company; check duplicate and unmatched customer mappings.

- Choose current open-deal stages and an exact invoice-payment interval.
- Normalize source currency units, then aggregate deals and qualifying invoices separately.
- Keep companies without matched invoices; distinguish a complete zero from missing billing coverage.

Tutorial: https://www.trycombined.com/resources/query-hubspot-and-stripe-with-ai
Synthetic SQL: https://www.trycombined.com/examples/hubspot-stripe-pipeline.sql

### HubSpot deals and unresolved Intercom conversations

Reporting unit: One row per CRM company; separate currencies for any monetary measure.

Resolve each conversation to its intended reporting company through explicit linkage or a reviewed bridge. Do not assign every contact-associated company to every conversation; leave ambiguous matches for review.

- Choose the customer-message interval and currently open conversations; internal updates and closed or snoozed conversations do not qualify for this example.
- Count distinct conversations, not messages, participants or joined deals.
- One company can have several conversations and deals; aggregate each record set first.

Tutorial: https://www.trycombined.com/resources/deals-and-support-conversations
Synthetic SQL: https://www.trycombined.com/examples/workflows/deals-and-support-conversations.sql
Expected result: https://www.trycombined.com/examples/workflows/deals-and-support-conversations.expected.json

## Decisions before running

- Exact reporting interval and observation date, including the timezone.
- Source accounts, live/test scope, required datasets and an acceptable freshness threshold.
- Maintained identity mappings and the treatment of duplicate or unmatched records.
- These are separate tested pair examples. Select one analysis first, or agree a shared reporting unit before composing them; no combined multi-app SQL fixture has been tested here.

## Agent assignment

```text
Use my authorized Combined MCP connection to plan this analysis: Which useful analyses can I run across these business apps?
Selected apps: HubSpot, Stripe, Intercom.
Use list_sources and list_datasets, following pagination on both, then describe_dataset to find the actual granted sources, logical dataset names and fields. Do not invent table names from the catalog.
Use get_freshness for the required sources, in batches of at most eight source IDs. An app can resolve to several Sources. Report any missing successful commit or date coverage before calculating.
Analysis: HubSpot pipeline and Stripe paid invoices.
Reporting unit: One row per CRM company and currency.
Map each scoped Stripe customer to its HubSpot company; check duplicate and unmatched customer mappings.
Choose current open-deal stages and an exact invoice-payment interval.
Normalize source currency units, then aggregate deals and qualifying invoices separately.
Keep companies without matched invoices; distinguish a complete zero from missing billing coverage.
Analysis: HubSpot deals and unresolved Intercom conversations.
Reporting unit: One row per CRM company; separate currencies for any monetary measure.
Resolve each conversation to its intended reporting company through explicit linkage or a reviewed bridge. Do not assign every contact-associated company to every conversation; leave ambiguous matches for review.
Choose the customer-message interval and currently open conversations; internal updates and closed or snoozed conversations do not qualify for this example.
Count distinct conversations, not messages, participants or joined deals.
One company can have several conversations and deals; aggregate each record set first.
Resolve these decisions before execution:
- Exact reporting interval and observation date, including the timezone.
- Source accounts, live/test scope, required datasets and an acceptable freshness threshold.
- Maintained identity mappings and the treatment of duplicate or unmatched records.
- These are separate tested pair examples. Select one analysis first, or agree a shared reporting unit before composing them; no combined multi-app SQL fixture has been tested here.
For a composed analysis, aggregate each independent record set before joining; never raw-join every selected app. Treat unmatched data separately from a verified empty result. Only add extra sources for an explicit context need.
Use read-only query_sql with discovered logical relations and parameterized values. Keep SQL at most 16 KiB and at most 100 parameters. Calculate over the complete eligible dataset before limiting the displayed answer to 50 rows (the tool limit is 1,000).
Return the decision table, exact definitions and time bounds, source freshness, mapping exceptions, supporting record references and query receipt when supplied. If literal text context is needed, use bounded search_context and state its coverage.
Return proposed follow-up actions for review; this plan does not authorize sending messages, changing records or adding source grants.
```

## Continue

Open this selection: https://www.trycombined.com/resources/business-data-mcp-planner#apps=hubspot%2Cstripe%2Cintercom&job=discover
Explore Combined: https://www.trycombined.com/
Connect your sources: https://www.trycombined.com/docs/getting-started/onboarding
MCP reference: https://www.trycombined.com/docs/integrations/mcp
