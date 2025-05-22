from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from agentic_kg.common.config import llm

from agentic_kg.tools import set_user_goal, list_import_files
from .sub_agents import file_suggestion_agent, schema_suggestion_agent


kg_construction_agent = LlmAgent(
    name="kg_construction_agent_v1",
    description="""Knowledge graph construction using Neo4j.""",
    model=llm,
    instruction="""You are an expert in knowledge graph construction using Neo4j.
        It relies on the 'user_goal' key in session state (which contains 'kind_of_graph' and 'graph_description') to determine what to do next.
        If 'user_goal' is not set, it will ask the user to specify their goal.
        If 'user_goal' is set, it will use the 'file_suggestion_agent' to suggest files
        that are most relevant for the kind of graph specified by the 'user_goal' key's 'kind_of_graph' field.

        <Tasks>
            1. Ask the user for their goal (kind_of_graph and graph_description), then use the set_user_goal tool to store it.
            2. If the 'user_goal' key has been set, use the tool 'suggest_import_files' to find out what to use.
            3. If the 'current_file_list' key has been set, use the tool 'schema_suggestion_agent' to suggest a schema.
        </Tasks>
        """,
    tools=[set_user_goal, list_import_files, AgentTool(file_suggestion_agent), AgentTool(schema_suggestion_agent)],
)

root_agent = kg_construction_agent