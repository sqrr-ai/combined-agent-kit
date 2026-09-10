# Business-data workflow examples

These eight read-only SQL fixtures use synthetic records and normalized teaching tables. They run in DuckDB without a source connection. Table and field aliases are examples, not the names of your actual Combined datasets.

Run a fixture in DuckDB, then compare its output with the matching `.expected.json` file. In a live workspace, discover the granted sources and logical schemas first, verify customer mappings and coverage, and adapt the calculation to the agreed metric.

| Fixture | What the example checks |
|---|---|
| `account-renewals-and-billing.sql` | Upcoming term ends and overdue invoice balances are aggregated separately; scheduled cancellation remains visible. |
| `activation-and-paid-retention.sql` | Account-level activation, repeated events, half-open service intervals and positive paid recurring coverage. |
| `customer-revenue-and-support-load.sql` | Closed-won booked value versus current unresolved ticket load, including older unresolved tickets. |
| `deals-and-support-conversations.sql` | Customer messages are reduced to conversation grain; recent internal updates do not qualify. |
| `opportunities-and-paid-invoices.sql` | Open pipeline, paid invoices, outstanding balance, overdue balance and undated balances remain distinct. |
| `renewal-pipeline-and-subscriptions.sql` | A subscription needs an explicit open renewal-deal relationship; expansion and closed deals do not cover it. |
| `sales-deals-and-unpaid-invoices.sql` | Remaining decimal balances, partial payments and child-customer mapping; no cents conversion for these example amounts. |
| `support-backlog-and-renewals.sql` | Seven complete days of ticket age, numeric Freshdesk states/priorities and an unknown count when mapping is absent. |

The fixtures were executed with DuckDB 1.5.5 and checked against independently specified expected results. The examples do not report customer outcomes or a live connection test.

Read the complete workflow guides at [Combined resources](https://www.trycombined.com/resources), browse [connector references](https://www.trycombined.com/connectors), or [connect your business data](https://www.trycombined.com/).
