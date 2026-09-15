# Combined business-data MCP examples

Use the guide matching your runtime:
- https://www.trycombined.com/resources/crewai-business-data-mcp
- https://www.trycombined.com/resources/langgraph-business-data-mcp

Checked September 15, 2026 with Python 3.12.11. Install each bundle in a separate virtual environment using its requirements file. These files pin the top-level packages; they are not a complete transitive lockfile. CrewAI uses MCP 1.28.x, while this LangGraph/FastMCP example uses MCP 2.x.

The verify_*.py scripts use synthetic MCP tools and no paid model or Combined account. Run the verification script alongside its matching *_combined.py file. CrewAI starts a local stdio subprocess; LangGraph uses an in-memory server and a scripted model. The adjacent verification JSON records the observed local result. The intentional LangGraph error-status check may print a tool error before the successful final JSON.

Local checks establish the documented adapter/configuration behavior. They do not test an authenticated Combined HTTP connection, source sync, a real account grant or a live model answer. The CrewAI check confirms its native client returns the first text block, without a separate structured result. The LangGraph check confirms a structured tool artifact, including data.receiptId, survives the graph loop. The new langchain.mcp module is beta.

For your real run, supply COMBINED_ACCOUNT_ID, COMBINED_TOKEN, BUSINESS_QUESTION and the model variable for your runtime (CREWAI_MODEL or LANGCHAIN_MODEL). Install/configure the selected model provider separately. Keep credentials in your runtime's secret configuration. The account must contain successfully synced sources, and the credential's own identity must have the necessary data grants.

The example task discovers schemas and mapping keys before querying. It requests bounded results, preserves unmatched records and separate currencies, and reports missing evidence. The scripts do not assume that sample fixture tables exist in your account.

Combined MCP wraps the QueryResult in structured_content.data. The script retains that full payload and extracts its receiptId. The separate QueryReceipt API supplies the recorded account/source/dataset scope; get_freshness supplies source sync timestamps. The example does not fetch the QueryReceipt endpoint.
