from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .variants import variants

AGENT_NAME = "relevant_fact_agent_v1"
relevant_fact_agent = Agent(
    name=AGENT_NAME,
    description="Proposes the kind of relevant facts that could be extracted from text files.",
    model=llm,
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

root_agent = relevant_fact_agent