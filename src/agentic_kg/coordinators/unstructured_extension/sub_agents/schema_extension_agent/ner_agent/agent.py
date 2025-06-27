from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .variants import variants

AGENT_NAME = "ner_schema_agent_v1"
ner_schema_agent = Agent(
    name=AGENT_NAME,
    description="Proposes the kind of named entities that could be extracted from text files.",
    model=llm,
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

root_agent = ner_schema_agent