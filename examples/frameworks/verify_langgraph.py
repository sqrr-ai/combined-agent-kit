"""No-account check of MCP adaptation and LangGraph structured-result handling.

Run beside langgraph_combined.py with langgraph-requirements.txt installed.
Uses an in-memory synthetic MCP server and scripted messages, not a model.
"""
import asyncio
import json

from fastmcp import FastMCP
from langchain.messages import AIMessage, HumanMessage
from langchain.mcp import MCPAdapter

from langgraph_combined import ALLOWED, build_graph, query_results, select_tools


class ScriptedModel:
    def bind_tools(self, tools):
        assert {tool.name for tool in tools} == set(ALLOWED)
        return self

    async def ainvoke(self, messages):
        if messages[-1].type == "human":
            return AIMessage(content="", tool_calls=[{
                "name": "query_sql", "args": {"maxRows": 20},
                "id": "synthetic-query-1", "type": "tool_call",
            }])
        return AIMessage(content="Synthetic tool call completed; inspect its artifact.")


async def main():
    server = FastMCP("Combined tutorial fixture")
    expected = {"data": {
        "receiptId": "00000000-0000-4000-8000-000000000001",
        "columns": [{"name": "company", "type": "VARCHAR"},
                    {"name": "currency", "type": "VARCHAR"},
                    {"name": "paid", "type": "INTEGER"}],
        "rows": [{"company": "Atlas", "currency": "USD", "paid": 5000}],
        "rowCount": 1, "truncated": False, "durationMs": 1,
        "estimatedInputBytes": None, "grantVersion": 1,
    }}

    @server.tool
    def query_sql(maxRows: int) -> dict:
        """Return the synthetic QueryResult wrapper; no SQL engine or real account is used."""
        if maxRows < 1:
            raise ValueError("maxRows must be positive")
        return expected

    for name in ALLOWED:
        if name != "query_sql":
            server.tool(lambda: {"fixture": True}, name=name)
    server.tool(lambda: "not allowed", name="delete_record")

    async with MCPAdapter(server) as adapter:
        discovered = await adapter.list_tools()
        tools = select_tools(discovered)
        assert "delete_record" not in {tool.name for tool in tools}
        graph = build_graph(tools, ScriptedModel())
        result = await graph.ainvoke({"messages": [HumanMessage(content="Run the fixture")]})
        results = query_results(result["messages"])
        assert len(results) == 1 and results[0]["status"] == "success"
        assert results[0]["structured_content"] == expected
        assert results[0]["receipt_id"] == expected["data"]["receiptId"]
        query = next(tool for tool in tools if tool.name == "query_sql")
        error = await query.ainvoke({"name": "query_sql", "args": {"maxRows": 0},
                                    "id": "synthetic-error", "type": "tool_call"})
        assert error.status == "error"
        try:
            select_tools([tool for tool in discovered if tool.name != "query_sql"])
        except RuntimeError:
            missing_rejected = True
        else:
            raise AssertionError("Missing query tool was not rejected")
    print(json.dumps({"passed": True, "checks": ["tool_allowlist", "graph_tool_loop",
        "structured_result_retained", "tool_error_status", "missing_tool_rejected"],
        "missing_tool_rejected": missing_rejected, "observed_query_result": results[0],
        "scope": "Synthetic in-memory MCP and scripted model; no live Combined or LLM call."}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
