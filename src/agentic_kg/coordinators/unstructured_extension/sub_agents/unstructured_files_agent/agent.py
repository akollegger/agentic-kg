from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .variants import variants

AGENT_NAME = "unstructured_files_agent_v1"
unstructured_files_agent = Agent(
    name=AGENT_NAME,
    description="Criticize the file list for relevance to the kind of graph indicated by the 'kind_of_graph' key in session state.",
    model=llm,
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"]
)

root_agent = unstructured_files_agent