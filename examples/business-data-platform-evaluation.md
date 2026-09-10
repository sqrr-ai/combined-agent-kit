# Business-data platform evaluation worksheet

Choose the connection and query setup that gets your agent to a useful business answer.

Prepared by Combined, September 10, 2026. Copy this worksheet for each candidate. Its numerical examples come from the linked synthetic DuckDB fixtures; blank result fields are for your own evaluation.

## 1. Define one decision

- Business question:
- Person who will use the answer:
- Selected apps and provider accounts:
- Existing warehouse, lakehouse or integration infrastructure you can reuse:
- Agent or client:
- Reporting unit, such as one company and currency:
- Exact reporting interval and observation time, including timezone:
- Maximum acceptable age of each source:
- Decision or next action this answer should support:

Use the [free business-data MCP planner](https://www.trycombined.com/resources/business-data-mcp-planner) to select two to four apps and get relevant tutorials, mapping checks and an agent assignment.

## 2. Record the work between the app and the answer

Fill each row with an actual component and its owner. Existing infrastructure counts as existing; record the additional work this project requires.

| Responsibility | Current component, if any | Candidate supplies | Your team adds | Verification |
| --- | --- | --- | --- | --- |
| Provider authorization and account selection | | | | |
| Required objects and fields | | | | |
| Initial ingestion and later updates | | | | |
| Storage or access to existing data | | | | |
| Identity map between applications | | | | |
| Business definitions and reporting unit | | | | |
| Query runtime or semantic analysis | | | | |
| Agent endpoint and authentication | | | | |
| Source, dataset and user access scope | | | | |
| Freshness and result evidence | | | | |
| Ongoing failures, changes and ownership | | | | |

For Combined, the [Source](https://www.trycombined.com/docs/product/sources), [access](https://www.trycombined.com/docs/product/access) and [MCP](https://www.trycombined.com/docs/integrations/mcp) references describe the managed connection-to-query path. Check current connector readiness, authorize the source, complete a successful sync, grant access and discover the real logical schema. Define customer mappings and metrics for your business.

## 3. Pick a worked answer contract

Each example has an executable teaching fixture and expected output. Start with its exact definitions; adapt relation names and SQL dialect for a different runtime. Production results depend on your authorized data and chosen reporting window.

### Salesforce and Stripe: pipeline, payments and unpaid balances

[Workflow](https://www.trycombined.com/resources/opportunities-and-paid-invoices) · [SQL](https://www.trycombined.com/examples/workflows/opportunities-and-paid-invoices.sql) · [Expected output](https://www.trycombined.com/examples/workflows/opportunities-and-paid-invoices.expected.json)

In the USD fixture, Atlas has 20,000 in open pipeline, 3,000 paid in the selected window, 700 outstanding, 500 overdue and 200 with no due date. Birch has 6,000 in pipeline and zero qualifying invoice amounts. Map billing customers to CRM accounts and aggregate opportunities and invoices separately. Keep outstanding, overdue and undated balances distinct.

- Observed output and supporting records:
- Mapping exceptions and missing coverage:
- Pass/fail against the fixture, then your production definition:

### Salesforce and Zendesk: account value and support backlog

[Workflow](https://www.trycombined.com/resources/customer-revenue-and-support-load) · [SQL](https://www.trycombined.com/examples/workflows/customer-revenue-and-support-load.sql) · [Expected output](https://www.trycombined.com/examples/workflows/customer-revenue-and-support-load.expected.json)

In the USD fixture, Atlas has 20,000 booked value and two unresolved tickets, one high or urgent. Birch has 15,000 booked value and no unresolved tickets. A ticket or comment must not multiply opportunity value. Resolve Zendesk organizations to reporting accounts; ticket counts are account context, including when monetary rows split by currency.

- Observed output and supporting records:
- Mapping exceptions and missing coverage:
- Pass/fail against the fixture, then your production definition:

### Salesforce and Chargebee: upcoming terms and overdue invoices

[Workflow](https://www.trycombined.com/resources/account-renewals-and-billing) · [SQL](https://www.trycombined.com/examples/workflows/account-renewals-and-billing.sql) · [Expected output](https://www.trycombined.com/examples/workflows/account-renewals-and-billing.expected.json)

Atlas has two upcoming terms and one overdue invoice with a 500 USD balance. Birch has one upcoming, non-renewing term and no overdue invoice. Aggregate terms and invoices separately at the account/currency level: repeating the same invoice per subscription would incorrectly double Atlas's balance. Preserve the Chargebee site/customer boundary and scheduled cancellations.

- Observed output and supporting records:
- Mapping exceptions and missing coverage:
- Pass/fail against the fixture, then your production definition:

### PostHog and Stripe: activation-to-paid retention

[Workflow](https://www.trycombined.com/resources/activation-and-paid-retention) · [SQL](https://www.trycombined.com/examples/workflows/activation-and-paid-retention.sql) · [Expected output](https://www.trycombined.com/examples/workflows/activation-and-paid-retention.expected.json)

The fixed fixture has three activated accounts, two paying at the baseline and one still covered by paid recurring service at the later checkpoint: 50% paid retention. Resolve event actors to product accounts and then billing customers. Deduplicate repeated events, retain the baseline denominator and use recurring invoice-line service intervals with `start <= checkpoint < end`. Active subscription status or a paid setup fee alone does not satisfy this definition.

- Observed output and supporting records:
- Mapping exceptions and missing coverage:
- Pass/fail against the fixture, then your production definition:

## 4. Run the evaluation and keep the evidence

1. Discover the accessible datasets, fields and account boundaries. Record the permissions used.
2. Verify the latest successful data commits and the complete interval needed by the question.
3. Inspect duplicate and unmatched identity mappings before combining records.
4. Execute the defined calculation over all eligible records, then limit the displayed result. Retain SQL, parameters, time bounds and result evidence.
5. Check zero-result, missing-source and revoked-access behavior in an authorized test scope.
6. Record the actual configuration time and components added. Compare the same answer contract across candidates.

| Candidate and configuration | Correct answer | Complete inputs | Access scope verified | Freshness met | Added setup | Evidence link |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |
| | | | | | | |

## 5. Compare a real month of operation

- Initial ingestion and recurring changed records:
- Destination storage and query compute:
- Semantic, search or agent features used:
- Integration-user, tool-call or contract charges, if applicable:
- Operational ownership and observed maintenance:
- Included trial allowance and applicable terms:

Record the relevant vendor prices and date with the usage assumptions. A record, tool call, connected user and compute unit measure different work. [Combined pricing](https://www.trycombined.com/pricing) documents its cardless 5-million-MAR start and current usage terms.

## 6. Choose the first useful connection

- Selected option and why it fits this project's starting point:
- Remaining prerequisite:
- Owner and next step:

Compare [Glean](https://www.trycombined.com/resources/combined-vs-glean), [Paragon](https://www.trycombined.com/resources/combined-vs-paragon), [Snowflake MCP](https://www.trycombined.com/resources/combined-vs-snowflake-mcp) and [Databricks MCP](https://www.trycombined.com/resources/combined-vs-databricks-mcp). Explore [Combined](https://www.trycombined.com/), [plan your apps](https://www.trycombined.com/resources/business-data-mcp-planner), or [start your workspace](https://platform.trycombined.com/onboarding/workspace).
