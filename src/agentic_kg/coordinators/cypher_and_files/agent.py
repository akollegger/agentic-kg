from google.adk.agents import Agent

from agentic_kg.sub_agents import cypher_agent, dataprep_agent
from agentic_kg.common.config import llm
from agentic_kg.tools import set_user_goal

from .prompts import instructions

AGENT_NAME = "cypher_and_files_agent_v1"
cypher_and_files_agent = Agent(
        name=AGENT_NAME,
        model=llm,
        description="Knowledge graph construction using specialized sub-agents for data preparation and cypher queries.", # Crucial for delegation later
        
        instruction=instructions[AGENT_NAME],
        tools=[set_user_goal], # Make the tool available to this agent
        sub_agents=[dataprep_agent, cypher_agent],
    )

# Export the root agent so adk can find it
root_agent = cypher_and_files_agent
