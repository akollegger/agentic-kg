from google.adk.agents import Agent

from agentic_kg.common.config import llm

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "dataprep_agent_v2"
dataprep_agent = Agent(
    name=AGENT_NAME,
    model=llm,
    description="Manages reading files and providing metadata about them.",
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

# Export the root agent so adk can find it
root_agent = dataprep_agent
