from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .tools import (
    sample_markdown_file,
)

from .prompts import return_instructions_unstructured_data

# Export the root agent so adk can find it
unstructured_data_agent = Agent(
    name="unstructured_data_agent_v1",
    model=llm,
    description="Analyzes unstructured data and creates a knowledge graph.", # Crucial for delegation later
    instruction=return_instructions_unstructured_data(),

    tools=[sample_markdown_file], 
)

# Export the root agent so adk can find it
root_agent = unstructured_data_agent
