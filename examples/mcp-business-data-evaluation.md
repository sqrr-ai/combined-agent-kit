# Business-data MCP evaluation kit

Published by Combined: https://www.trycombined.com/resources/best-mcp-servers-for-business-data

Use this worksheet to compare access to your own business records. It is an evaluation template, not a vendor benchmark.

## 1. Define the job

Question: Which companies have open sales opportunities, and what is the total amount paid on their paid invoices in the selected period?

Write down:
- CRM and billing accounts in scope.
- Exact start and end timestamps, timezone and currencies.
- Open/closed stage mapping.
- Shared company identifier and who maintains it.
- Required objects, fields and sync freshness.
- Whether you need read-only analysis or application writes.

## 2. Discover before calculating

Prompt:
"List my permitted CRM and billing datasets. Inspect their schemas and freshness. Identify company IDs, deal stages and amounts, invoice customer IDs, invoice status, amount paid, currency and payment timestamp. Explain the available cross-system customer mapping. Do not infer identity from names alone. Report missing fields or coverage."

## 3. Run the calculation

Prompt:
"Using those permitted datasets, aggregate open opportunities by company and currency. Separately aggregate paid invoices in the agreed time window by company and currency, then join those aggregates. Keep companies with open opportunities even when no matching paid invoice exists. Flag unmatched customer IDs and ambiguous mappings. Return the source timestamps, calculation definition, coverage limits and query receipt."

Check that two deals and two invoices do not double the invoice total. A complete runnable sample is at:
https://www.trycombined.com/examples/hubspot-stripe-pipeline.sql

## 4. Test the permission boundary

In an isolated test workspace, remove the relevant dataset grant and issue a new request for it. Record whether access is denied. Previously returned data can remain in the agent conversation; revoking a grant is not deletion of that conversation.

## 5. Compare the work you still own

| Check | Candidate A | Candidate B | Evidence |
|---|---|---|---|
| Required objects and custom fields | | | |
| Maintained customer mapping | | | |
| Correct complete-dataset totals | | | |
| Freshness visible in the answer | | | |
| New request denied after grant removal | | | |
| Ingestion and storage operation | | | |
| Query-service operation | | | |
| Estimated usage and model costs | | | |

## Try the workflow in Combined

1. Add the source in Connected Apps and complete its authorization.
2. Select datasets, run the first sync and check freshness.
3. Use Set up or Access to connect the agent and grant the intended datasets.
4. Discover logical relation names before running a bounded, read-only query.
5. Inspect the result, query receipt and coverage before adding another source.

Combined provides an initial 5 million MAR without a card. Usage after the trial is $5 per million MAR, prorated, with no monthly minimum. Current terms: https://www.trycombined.com/pricing
