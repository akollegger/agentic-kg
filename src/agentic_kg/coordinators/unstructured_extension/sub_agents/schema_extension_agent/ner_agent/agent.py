from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .variants import variants

AGENT_NAME = "unstructured_schema_agent_v1"
unstructured_schema_agent = Agent(
    name=AGENT_NAME,
    description="Proposes a knowledge graph schema based on the user goal and approved file list.",
    model=llm,
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

root_agent = unstructured_schema_agent