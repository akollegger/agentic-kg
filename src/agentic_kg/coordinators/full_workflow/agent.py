from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from agentic_kg.common.config import llm

from agentic_kg.tools import set_user_goal, get_user_goal, list_import_files
from .sub_agents import file_suggestion_agent, schema_suggestion_agent


full_workflow_agent = LlmAgent(
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
            2. If the user does not have a goal, you can use 'list_import_files' to show them available files.
            3. Only if the 'user_goal' key has been set, use tools to make suggestions for relevant files.
            4. If the 'suggested_file_list' key has been set, suggest a property graph schema for those files.
        </Tasks>
        """,
    tools=[list_import_files, set_user_goal, get_user_goal, AgentTool(file_suggestion_agent), AgentTool(schema_suggestion_agent)],
)

root_agent = full_workflow_agent