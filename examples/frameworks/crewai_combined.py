"""Combined + CrewAI example. See the adjacent requirements and guide."""
import os
from urllib.parse import urlencode
from uuid import UUID

from crewai import Agent, Crew, LLM, Task
from crewai.mcp import MCPServerHTTP
from crewai.mcp.filters import create_static_tool_filter


def build_crew(account_id, token, question, model):
    account_id = str(UUID(account_id))
    url = "https://platform.trycombined.com/mcp?" + urlencode({"account_id": account_id})
    allowed = [
        "list_sources", "list_datasets", "describe_dataset",
        "get_freshness", "query_sql",
    ]
    server = MCPServerHTTP(
        url=url,
        headers={"Authorization": f"Bearer {token}"},
        streamable=True,
        tool_filter=create_static_tool_filter(allowed_tool_names=allowed),
        cache_tools_list=False,
    )
    analyst = Agent(
        role="Business data analyst",
        goal="Answer from granted business data with an inspectable query trail",
        backstory="You inspect schemas and mappings before querying business data.",
        llm=model,
        mcps=[server],
        cache=False,
        allow_delegation=False,
        max_iter=20,
    )
    task = Task(
        description=(
            question + "\n"
            "First discover granted Sources and datasets, following pagination. "
            "Describe relevant datasets; check freshness. Use discovered relations "
            "and fields only. Explain the company/customer mapping. Aggregate each "
            "side before joining; preserve unmatched companies and currencies. "
            "Use bounded SELECT queries with parameters and maxRows=20. Return "
            "small aggregates. Report scope, SQL, parameters, UTC window, freshness "
            "and any truncation. If tools fail or evidence is missing, explain what "
            "is missing instead of producing a business total."
        ),
        expected_output=(
            "A bounded company/currency table with query details, mapping and "
            "unmatched-record notes, or a specific explanation of missing evidence."
        ),
        agent=analyst,
    )
    return Crew(agents=[analyst], tasks=[task], tracing=False)


def main():
    crew = build_crew(
        os.environ["COMBINED_ACCOUNT_ID"], os.environ["COMBINED_TOKEN"],
        os.environ["BUSINESS_QUESTION"], LLM(model=os.environ["CREWAI_MODEL"]),
    )
    print(crew.kickoff())


if __name__ == "__main__":
    main()
