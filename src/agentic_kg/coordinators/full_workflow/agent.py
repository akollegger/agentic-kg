from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from agentic_kg.common.config import llm

from agentic_kg.tools import set_kind_of_graph, list_import_files
from .sub_agents import file_suggestion_agent, schema_suggestion_agent


kg_construction_agent = LlmAgent(
    name="kg_construction_agent_v1",
    description="""Knowledge graph construction using Neo4j.""",
    model=llm,
    instruction="""You are an expert in knowledge graph construction using Neo4j.
        Your primary goal is to construct a knowledge graph using specific import files
        that are most relevant for the kind of graph specified by the 'kind_of_graph' key in session state.

        <Tasks>
            1. Ask the user what kind of graph they're interested in constructing, then use the set_kind_of_graph tool to set it.
            2. If the 'kind_of_graph' key has been set, use the tool 'suggest_import_files' to find out what to use.
            3. If the 'current_file_list' key has been set, use the tool 'schema_suggestion_agent' to suggest a schema.
        </Tasks>
        """,
    tools=[set_kind_of_graph, list_import_files, AgentTool(file_suggestion_agent), AgentTool(schema_suggestion_agent)],
)

root_agent = kg_construction_agent