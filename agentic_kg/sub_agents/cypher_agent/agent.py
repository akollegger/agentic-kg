from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from google.adk.models.lite_llm import LiteLlm

from agentic_kg.model_config import model_roles

from .tools import (
    neo4j_is_ready, 
    get_physical_schema, 
    read_neo4j_cypher,
    write_neo4j_cypher,
    reset_neo4j_data
)

from .prompts import return_instructions_cypher


# Export the root agent so adk can find it
cypher_agent = Agent(
    name="cypher_agent_v1",
    model=LiteLlm(model=model_roles["chat"]),
    description="Provides acccess to a Neo4j database through Cypher queries.", # Crucial for delegation later
    instruction=return_instructions_cypher(),

    tools=[neo4j_is_ready, get_physical_schema, read_neo4j_cypher, write_neo4j_cypher, reset_neo4j_data], # Make the tool available to this agent
)

# Export the root agent so adk can find it
root_agent = cypher_agent
