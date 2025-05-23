from google.adk.agents import Agent

from agentic_kg.common.config import llm
from agentic_kg.tools import finished

from .variants import variants

AGENT_NAME = "cypher_agent_v2"
cypher_agent = Agent(
    name=AGENT_NAME,
    model=llm,
    description="Provides acccess to a Neo4j database through Cypher queries. Able to read/write data and perform other database operations.", # Crucial for delegation later
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

# Export the root agent so adk can find it
root_agent = cypher_agent
