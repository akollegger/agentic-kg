from google.adk.agents import Agent

from agentic_kg.common.config import llm
from agentic_kg.sub_agents import cypher_agent

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "just_cypher_agent_v2"
just_cypher_agent = Agent(
        name=AGENT_NAME,
        model=llm,
        description="Knowledge graph construction using Neo4j and cypher.", # Crucial for delegation later
        
        instruction=variants[AGENT_NAME]["instruction"],
        tools=variants[AGENT_NAME]["tools"], # Make the tool available to this agent
        sub_agents=[cypher_agent]
    )

root_agent = just_cypher_agent