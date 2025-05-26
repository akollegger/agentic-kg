from google.adk.agents import Agent

from agentic_kg.common.config import llm

from .sub_agents import cypher_agent, dataprep_agent

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "cypher_and_files_agent_v2"
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
