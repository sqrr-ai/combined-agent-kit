"""No-account check of CrewAI configuration and local MCP text results.

Run beside crewai_combined.py with crewai-requirements.txt installed.
The child process serves a synthetic fixture on stdio. No model is called.
"""
import asyncio
import json
import os
from pathlib import Path
import sys

os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"


def serve_fixture():
    from mcp.server.fastmcp import FastMCP
    from mcp.types import CallToolResult, TextContent
    server = FastMCP("Combined synthetic text-result fixture")

    @server.tool()
    def query_sql() -> CallToolResult:
        """Return deliberately different text and structured synthetic fields."""
        return CallToolResult(
            content=[TextContent(type="text", text="Synthetic Atlas paid amount: USD 5000")],
            structuredContent={"fixture": True, "private_to_artifact": "structured-only"},
        )

    @server.tool()
    def delete_record() -> str:
        """Excluded fixture tool. It has no side effects."""
        return "excluded"
    server.run(transport="stdio")


async def check():
    from crewai import BaseLLM
    from crewai.mcp.client import MCPClient
    from crewai.mcp.transports import StdioTransport
    from crewai_combined import build_crew

    class NeverCalledModel(BaseLLM):
        def call(self, *args, **kwargs):
            raise AssertionError("The configuration check must not call a model")

    crew = build_crew("00000000-0000-4000-8000-000000000001", "synthetic-placeholder",
                      "Inspect synthetic data", NeverCalledModel(model="fixture"))
    config = crew.agents[0].mcps[0]
    assert config.url.endswith("account_id=00000000-0000-4000-8000-000000000001")
    assert config.headers["Authorization"] == "Bearer synthetic-placeholder"
    assert config.streamable and not config.cache_tools_list
    transport = StdioTransport(command=sys.executable, args=[str(Path(__file__).resolve()), "--server"])
    async with MCPClient(transport=transport) as client:
        discovered = await client.list_tools()
        selected = [tool for tool in discovered if config.tool_filter(tool)]
        assert [tool["name"] for tool in selected] == ["query_sql"]
        text = await client.call_tool("query_sql", {})
        assert str(text) == "Synthetic Atlas paid amount: USD 5000", repr(text)
        assert "structured-only" not in str(text)
    print(json.dumps({"passed": True, "checks": ["crew_constructed", "account_url",
        "bearer_header", "local_mcp_discovery", "tool_allowlist", "text_result_observed"],
        "observed_text": str(text), "structured_content_returned_by_native_client": False,
        "scope": "Synthetic local stdio MCP and configuration; no live HTTP, Combined or LLM call."}, indent=2))


if __name__ == "__main__":
    if sys.argv[1:] == ["--server"]:
        serve_fixture()
    else:
        asyncio.run(check())
