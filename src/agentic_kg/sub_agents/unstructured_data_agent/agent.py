from google.adk.agents import Agent

from agentic_kg.common.config import llm

# variants are pairs of instructions with tools
from .variants import variants   

AGENT_NAME = "unstructured_data_agent_v1"
unstructured_data_agent = Agent(
    name=AGENT_NAME,
    model=llm,
    description="Analyzes unstructured data and creates a knowledge graph.", # Crucial for delegation later
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

# Export the root agent so adk can find it
root_agent = unstructured_data_agent
