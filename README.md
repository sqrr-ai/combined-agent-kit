# Combined business-data agent kit

Give your coding agent a practical playbook for CRM, billing, customer context and cross-app analysis.

[Combined](https://www.trycombined.com/) connects your business apps to the agent you already use. Start with 5 million MAR without a card; after the trial, usage is $5 per million MAR with no monthly minimum. Combined offers **1,125 connectors**, including connectors generated through desktop automation.

## Install

```sh
npx skills add sqrr-ai/combined-agent-kit
```

Select the skills and agents you want to use. Connect your Combined workspace through its Set up or Access flow. Installing a skill supplies instructions; your own source connections and grants determine the data available.

[Connect your first source](https://www.trycombined.com/) · [Connector guides](https://www.trycombined.com/connectors) · [MCP setup](https://www.trycombined.com/docs/integrations/mcp) · [Pricing](https://www.trycombined.com/pricing)

## Six practical skills

| Skill | What it helps you do |
|---|---|
| [Agent setup](skills/combined-agent-setup/SKILL.md) | Connect an MCP client and check account scope, authentication and granted sources. |
| [Business data](skills/combined-business-data/SKILL.md) | Discover relevant datasets, choose SQL or text retrieval and answer a cross-app question. |
| [HubSpot + Stripe](skills/combined-hubspot-stripe/SKILL.md) | Compare open CRM pipeline with paid invoices using an explicit customer mapping. |
| [Customer context](skills/combined-customer-context/SKILL.md) | Build a customer brief from CRM, billing, support and conversation records. |
| [Read-only SQL](skills/combined-readonly-sql/SKILL.md) | Query granted datasets with bounded joins, aggregates and checkable receipts. |
| [Revenue analysis](skills/combined-revenue-analysis/SKILL.md) | Define and reconcile billing and CRM metrics, with clear currencies and reporting windows. |

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
