from google.adk.agents import Agent

from agentic_kg.sub_agents import cypher_agent, dataprep_agent
from agentic_kg.common.config import llm

from .prompts import instructions

cypher_and_files_agent = Agent(
        name="kg_agent_v2",
        model=llm,
        description="Knowledge graph construction using specialized sub-agents for data preparation and cypher queries.", # Crucial for delegation later
        
        instruction=instructions["cypher_and_files_v1"],
        tools=[], # Make the tool available to this agent
        sub_agents=[cypher_agent, dataprep_agent],
    )

# Export the root agent so adk can find it
root_agent = cypher_and_files_agent
