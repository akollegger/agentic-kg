from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .variants import variants

AGENT_NAME = "schema_suggestion_agent_v1"
schema_suggestion_agent = Agent(
    name=AGENT_NAME,
    description="Suggests a knowledge graph schema based on the user goal and suggested file list.",
    model=llm,
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
    output_key="proposed_schema"
)

root_agent = schema_suggestion_agent