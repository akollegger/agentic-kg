from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import ToolContext

from agentic_kg.common.config import llm
from agentic_kg.common.util import tool_success

from agentic_kg.sub_agents.dataprep_agent.tools import list_import_files, sample_file

from pydantic import BaseModel, Field

schema_suggestion_agent = Agent(
    name="schema_suggestion_agent",
    description="Suggests a knowledge graph schema based on the kind_of_graph and the current_file_list.",
    model=llm,
    instruction="""You are an expert at knowledge graph modeling for property graphs. Propose an appropriate
    schema for the kind of graph '{{kind_of_graph}}' based on the list of files '{{current_file_list}}'.

    """,
    tools=[sample_file],
    output_key="proposed_schema"
)

root_agent = schema_suggestion_agent