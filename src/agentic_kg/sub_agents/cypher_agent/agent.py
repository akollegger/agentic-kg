from google.adk.agents import Agent

from agentic_kg.common.config import llm

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
    model=llm,
    description="Provides acccess to a Neo4j database through Cypher queries. Able to read/write data and answer configuration questions like the location of the import directory.", # Crucial for delegation later
    instruction=return_instructions_cypher(),

    tools=[neo4j_is_ready, get_physical_schema, read_neo4j_cypher, write_neo4j_cypher, reset_neo4j_data], # Make the tool available to this agent
)

# Export the root agent so adk can find it
root_agent = cypher_agent
