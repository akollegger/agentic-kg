from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .tools import (
    sample_markdown_file,
)

from .prompts import instructions   

AGENT_NAME = "unstructured_data_agent_v1"
unstructured_data_agent = Agent(
    name=AGENT_NAME,
    model=llm,
    description="Analyzes unstructured data and creates a knowledge graph.", # Crucial for delegation later
    instruction=instructions[AGENT_NAME],

    tools=[sample_markdown_file], 
)

# Export the root agent so adk can find it
root_agent = unstructured_data_agent
