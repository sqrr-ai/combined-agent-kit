"""Combined + LangGraph with separately inspectable MCP query results and receipt IDs."""
import asyncio
import json
import os
from urllib.parse import urlencode
from uuid import UUID

from fastmcp.client import Client
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langchain.mcp import MCPAdapter
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

ALLOWED = (
    "list_sources", "list_datasets", "describe_dataset",
    "get_freshness", "query_sql",
)
INSTRUCTIONS = (
    "Answer only from the granted business data. Discover Sources and datasets "
    "with pagination, inspect schemas and check freshness before querying. "
    "Use discovered relations and explicit company/customer mapping keys. "
    "Aggregate each side before joining; preserve unmatched rows and currencies. "
    "Use parameterized, bounded SELECT queries with maxRows=20. Report source "
    "scope, query, UTC window, mapping, freshness and truncation. Tool errors "
    "or missing evidence must be reported rather than replaced by guessed totals."
)

def select_tools(discovered_tools):
    discovered = {tool.name: tool for tool in discovered_tools}
    missing = set(ALLOWED) - discovered.keys()
    if missing:
        raise RuntimeError(f"Missing MCP tools: {sorted(missing)}")
    return [discovered[name] for name in ALLOWED]


def query_results(messages):
    results = []
    for message in messages:
        if isinstance(message, ToolMessage) and message.name == "query_sql":
            artifact = message.artifact if isinstance(message.artifact, dict) else {}
            payload = artifact.get("structured_content")
            data = payload.get("data") if isinstance(payload, dict) else None
            results.append({
                "tool_call_id": message.tool_call_id, "status": message.status,
                "receipt_id": data.get("receiptId") if isinstance(data, dict) else None,
                "structured_content": payload,
            })
    return results


def build_graph(tools, model):
    bound_model = model.bind_tools(tools)

    async def answer(state: MessagesState):
        response = await bound_model.ainvoke(
            [SystemMessage(content=INSTRUCTIONS), *state["messages"]]
        )
        return {"messages": [response]}

    def next_step(state: MessagesState):
        return "tools" if state["messages"][-1].tool_calls else END

    builder = StateGraph(MessagesState)
    builder.add_node("answer", answer)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "answer")
    builder.add_conditional_edges(
        "answer", next_step, {"tools": "tools", END: END}
    )
    builder.add_edge("tools", "answer")
    return builder.compile()

async def main():
    account_id = str(UUID(os.environ["COMBINED_ACCOUNT_ID"]))
    url = "https://platform.trycombined.com/mcp?" + urlencode(
        {"account_id": account_id}
    )
    client = Client(url, auth=os.environ["COMBINED_TOKEN"])
    async with MCPAdapter(client) as adapter:
        tools = select_tools(await adapter.list_tools())
        model = init_chat_model(os.environ["LANGCHAIN_MODEL"])
        graph = build_graph(tools, model)
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=os.environ["BUSINESS_QUESTION"])]},
            config={"recursion_limit": 40},
        )
        print(result["messages"][-1].content)
        print(json.dumps(query_results(result["messages"]), default=str))

if __name__ == "__main__":
    asyncio.run(main())
