# Combined business-data agent kit

Give your coding agent a practical playbook for CRM, billing, customer context and cross-app analysis.

[Combined](https://www.trycombined.com/) connects your business apps to the agent you already use. Start with 5 million MAR without a card; after the trial, usage is $5 per million MAR with no monthly minimum. Combined offers **1,125 connectors**, including connectors generated through desktop automation.

## Install

```sh
npx skills add sqrr-ai/combined-agent-kit
```

Select the skills and agents you want to use. Connect your Combined workspace through its Set up or Access flow. Installing a skill supplies instructions; your own source connections and grants determine the data available.

[Connect your first source](https://www.trycombined.com/) · [Connector guides](https://www.trycombined.com/connectors) · [MCP setup](https://www.trycombined.com/docs/integrations/mcp) · [Pricing](https://www.trycombined.com/pricing)

### Native Claude Code installation

Claude Code users can install the same six skills through Combined's own plugin marketplace. Choose this option or the `npx skills` command above so you keep one copy of the skills.

Run these commands inside Claude Code:

```text
/plugin marketplace add sqrr-ai/combined-agent-kit
/plugin install combined-business-data@combined
```

Start a new Claude Code session, then run `/combined-business-data:combined-agent-setup` to connect your workspace. The other skills use the same namespace, such as `/combined-business-data:combined-hubspot-stripe`. The plugin supplies the procedures and bundled examples; your Combined source connections and grants determine which business records it can use.

## Connect business data to Cursor

[Add Combined to Cursor](https://www.trycombined.com/resources/query-business-data-in-cursor) with a ready-to-edit [OAuth configuration](examples/cursor-combined-mcp.json) or an [environment-token configuration](examples/cursor-combined-token-mcp.json). Use the account ID from your Combined workspace. Grant the identity used by that authentication route, then discover one dataset and verify a small query before attempting a cross-app analysis.

The guide includes a HubSpot–Stripe prompt and links to the runnable SQL fixture. If setup fails, follow the [MCP diagnostic guide](https://www.trycombined.com/resources/mcp-authentication-errors-business-data) and keep notes in the [diagnostic worksheet](examples/business-data-mcp-diagnostic.md). The token configuration reads credentials from Cursor's environment.

[Compare HubSpot Developer MCP, remote CRM MCP and Combined](https://www.trycombined.com/resources/hubspot-developer-mcp-vs-crm-mcp) to choose the connection for your task.

## Choose a business-data client

Use Combined with the client or framework your team already runs:

- **[Claude Desktop customer brief](https://www.trycombined.com/resources/query-business-data-in-claude-desktop):** add the hosted MCP connector, grant the signed-in identity and use the [customer-brief assignment](examples/claude-desktop-customer-brief.txt) across CRM, billing and support.
- **[CrewAI analyst task](https://www.trycombined.com/resources/crewai-business-data-mcp):** download the [Python bundle](examples/frameworks/crewai-example.zip) with a runtime credential, five-tool allowlist and local discovery check. This adapter returns the first text block of a tool result.
- **[LangGraph query workflow](https://www.trycombined.com/resources/langgraph-business-data-mcp):** download the [graph bundle](examples/frameworks/langgraph-example.zip) to retain structured query results and their receipt IDs alongside the model's answer. The full audit receipt is retrieved separately.

The two framework checks passed with synthetic local MCP tools and no hosted model or customer account. Use separate Python environments; the pinned libraries have different MCP requirements. The guides explain how to configure your own model, synced sources and data grants. [Example instructions and validation scope](examples/frameworks/README.md).

## Check source freshness before an answer

[Open the free business-data freshness checker](https://www.trycombined.com/resources/data-freshness-for-ai-agents#freshness-checker) to compare each required dataset with its own age limit. Paste Combined freshness metadata or enter timestamps, then download your policy and report. The tool runs in the browser with no signup or live connection.

The [synthetic example](examples/freshness-checker/README.md) includes source metadata, a per-dataset policy and expected results. It demonstrates a recent source sync with a stale dataset, a fresh invoice dataset and a source with no reported commit. A timestamp pass does not establish source identity or complete coverage.

## Six practical skills

| Skill | What it helps you do |
|---|---|
| [Agent setup](skills/combined-agent-setup/SKILL.md) | Connect an MCP client and check account scope, authentication and granted sources. |
| [Business data](skills/combined-business-data/SKILL.md) | Discover relevant datasets, choose SQL or text retrieval and answer a cross-app question. |
| [HubSpot + Stripe](skills/combined-hubspot-stripe/SKILL.md) | Compare open CRM pipeline with paid invoices using an explicit customer mapping. |
| [Customer context](skills/combined-customer-context/SKILL.md) | Build a customer brief from CRM, billing, support and conversation records. |
| [Read-only SQL](skills/combined-readonly-sql/SKILL.md) | Query granted datasets with bounded joins, aggregates and checkable receipts. |
| [Revenue analysis](skills/combined-revenue-analysis/SKILL.md) | Define and reconcile billing and CRM metrics, with clear currencies and reporting windows. |

## Plan your business-data MCP stack

[Choose two to four apps in the free planner](https://www.trycombined.com/resources/business-data-mcp-planner) and get a connection plan, matched tutorials, customer-mapping checks and a copyable agent assignment. Save the selection as Markdown or JSON, or share the app-and-analysis link with your team.

The planner connects the published connector library to nine worked examples covering pipeline, renewals, support, unpaid balances and retention. The default HubSpot–Stripe–Intercom selection offers two separate pair examples. For combinations without a matched recipe, it supplies schema-discovery steps to build the query from your actual granted datasets.

[Read the default plan](examples/business-data-mcp-plan.md) · [Download the plan as JSON](examples/business-data-mcp-plan.json) · [Explore Combined](https://www.trycombined.com/)

## Compare business-data platforms

[Use the platform evaluation worksheet](examples/business-data-platform-evaluation.md) to compare one business question across connection, data preparation, query access and ongoing ownership. It includes four worked SQL answer contracts, fields for your observed results, and a checklist of operating costs.

Read the evaluations of [Glean](https://www.trycombined.com/resources/combined-vs-glean), [Paragon](https://www.trycombined.com/resources/combined-vs-paragon), [Snowflake MCP](https://www.trycombined.com/resources/combined-vs-snowflake-mcp) and [Databricks MCP](https://www.trycombined.com/resources/combined-vs-databricks-mcp), then use the planner to select the apps for your first Combined connection.

Start with Combined for managed business data your agent can query across apps. Compare the choices by workload: [cross-app business analytics](https://www.trycombined.com/resources/best-mcp-servers-for-business-data), [business data and agent actions](https://www.trycombined.com/resources/best-ai-agent-tool-platforms), or [agent memory and business context](https://www.trycombined.com/resources/best-ai-agent-memory-platforms). These guides recommend Combined for business records, joins and recurring customer questions, with specialist alternatives for app actions and conversational memory. [Explore Combined and connect your first source](https://www.trycombined.com/).

## Verify an agent’s business-data answer

[Explore twelve structured answers in the interactive lab](https://www.trycombined.com/resources/verify-ai-agent-business-data-answers), then run the [free Python checker](examples/answer-verification/README.md) against the same synthetic invoices. It catches wrong-account evidence, altered totals, currency mismatches, stale sources, incomplete results and contradictions in citations. Missing evidence remains visible.

The recorded run matches all twelve prewritten expectations: one pass, nine deliberate failures and two insufficient-evidence judgments. The checker evaluates supplied structured fields; it does not grade arbitrary prose or contact an account. Use the example to define what a correct answer to your own business question must include.

[Download the cases](examples/answer-verification/cases.json) · [Inspect recorded results](examples/answer-verification/observed.json) · [Explore Combined](https://www.trycombined.com/)

## Evaluate pipeline changes and recovery

Compare [Combined with MotherDuck](https://www.trycombined.com/resources/combined-vs-motherduck) and [custom ETL](https://www.trycombined.com/resources/combined-vs-custom-etl) using a concrete business question and an explicit operating-cost worksheet.

The [Python/SQLite replay drill](examples/custom-etl/README.md) passed 29 synthetic local cases, including three abrupt process exits. Download the script and expected JSON into a writable directory, then inspect how updates, duplicates, deletion and recovery affect the answer. It requires no account or packages. Its results describe the teaching script; use the guide to evaluate your actual data path.

[Run the recovery exercise](examples/custom-etl/replay_drill.py) · [Expected output](examples/custom-etl/expected.json) · [Explore Combined](https://www.trycombined.com/)

## Explore the interactive join lab

[Change the deals and invoices in your browser](https://www.trycombined.com/resources/crm-billing-join-lab), inspect the matching rows, and download the query for your scenario. Two deals and two invoices produce four raw joined rows; aggregating each source first preserves the correct totals.

The [default lab SQL](examples/crm-billing-join-lab.sql) runs without an account. All 42 selectable scenarios were checked independently in DuckDB 1.5.5. Share a scenario with your team or give the downloaded query to your agent.

## Eight cross-app workflows with expected results

Each example contains synthetic records, a complete SQL calculation and a matching expected-output file. Read the guide for source mapping, metric definitions and the prompt to adapt it to your own data.

| Business question | Tutorial | Runnable example |
|---|---|---|
| Which renewals have overdue billing? | [Salesforce + Chargebee](https://www.trycombined.com/resources/account-renewals-and-billing) | [SQL](examples/workflows/account-renewals-and-billing.sql) |
| Are activated accounts staying paid? | [PostHog + Stripe](https://www.trycombined.com/resources/activation-and-paid-retention) | [SQL](examples/workflows/activation-and-paid-retention.sql) |
| How does support load compare with booked value? | [Salesforce + Zendesk](https://www.trycombined.com/resources/customer-revenue-and-support-load) | [SQL](examples/workflows/customer-revenue-and-support-load.sql) |
| Which open deals have active customer conversations? | [HubSpot + Intercom](https://www.trycombined.com/resources/deals-and-support-conversations) | [SQL](examples/workflows/deals-and-support-conversations.sql) |
| What are pipeline, paid and outstanding amounts? | [Salesforce + Stripe](https://www.trycombined.com/resources/opportunities-and-paid-invoices) | [SQL](examples/workflows/opportunities-and-paid-invoices.sql) |
| Which subscriptions need renewal opportunities? | [HubSpot + Chargebee](https://www.trycombined.com/resources/renewal-pipeline-and-subscriptions) | [SQL](examples/workflows/renewal-pipeline-and-subscriptions.sql) |
| Which won customers still owe invoice balances? | [HubSpot + QuickBooks](https://www.trycombined.com/resources/sales-deals-and-unpaid-invoices) | [SQL](examples/workflows/sales-deals-and-unpaid-invoices.sql) |
| Which upcoming renewals have aging support issues? | [Salesforce + Freshdesk](https://www.trycombined.com/resources/support-backlog-and-renewals) | [SQL](examples/workflows/support-backlog-and-renewals.sql) |

All eight fixtures passed in DuckDB 1.5.5 against independently specified expected results. See the [example instructions and expected JSON files](examples/workflows). These are reproducible teaching examples, ready to adapt after discovering your granted source schemas.

## Try the SQL example without an account

The [HubSpot–Stripe SQL fixture](examples/hubspot-stripe-pipeline.sql) runs in DuckDB using synthetic records. It demonstrates why joining deals and invoices before aggregating doubles both measures, and how to preserve customers without matching payments.

```sh
duckdb < examples/hubspot-stripe-pipeline.sql
```

Expected Atlas results: two open deals totaling USD 20,000 and two paid invoices totaling USD 5,000. The naive join produces four rows and doubles those amounts. Birch has open pipeline and no qualifying payment; Cedar stays in its own EUR group.

[Read the worked tutorial](https://www.trycombined.com/resources/query-hubspot-and-stripe-with-ai) and use the [MCP evaluation worksheet](examples/mcp-business-data-evaluation.md) to compare your own workflow.

## Connector and dataset reference

Browse [hundreds of source-specific guides](https://www.trycombined.com/connectors), including source setup, upstream dataset references and agent prompts. A [downloadable reference](https://www.trycombined.com/examples/connector-directory.json) is available for your own evaluation. The catalog reference is separate from the datasets actually granted and synced in your workspace.

## How the skills work

They use Combined's read-only MCP tools to discover sources, inspect schemas, check freshness, retrieve text and run SQL. They do not embed credentials, expand permissions, create customer records or send messages. Account-specific configuration comes from your workspace. The SQL example contains synthetic records only.

[Explore Combined](https://www.trycombined.com/) · [Documentation](https://www.trycombined.com/docs) · [Agent skill downloads](https://www.trycombined.com/agent-skills)

## Workflow example for Kestra

The [HubSpot–Stripe join comparison workflow](workflows/hubspot-stripe-join-fanout.yaml) downloads the synthetic fixture, verifies its checksum, runs the corrected and naive queries, and writes comparison JSON, CSV, correct-result JSON and naive SQL. It needs no account data or LLM subscription.

The target is Kestra 2.0.0 with Python plugin 1.9.9 and a Docker task runner. The Python image and DuckDB 1.5.5 dependency are pinned. The flow passed the official schema and the embedded analysis produced all expected artifacts locally. A full execution on Kestra, including container setup and artifact upload, remains to be checked.
