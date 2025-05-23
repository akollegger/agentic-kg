from google.adk.agents import Agent

from agentic_kg.sub_agents import cypher_agent, dataprep_agent
from agentic_kg.common.config import llm

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "cypher_and_files_agent_v1"
cypher_and_files_agent = Agent(
        name=AGENT_NAME,
        model=llm,
        description="Knowledge graph construction using specialized sub-agents for data preparation and cypher queries.", # Crucial for delegation later
        
        instruction=variants[AGENT_NAME]["instruction"],
        tools=variants[AGENT_NAME]["tools"], # Make the tool available to this agent
        sub_agents=[dataprep_agent, cypher_agent],
    )

# Export the root agent so adk can find it
root_agent = cypher_and_files_agent
