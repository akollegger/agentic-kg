from google.adk.agents import Agent

from agentic_kg.common.config import llm
from agentic_kg.tools import finished

from .tools import (
    neo4j_is_ready, 
    get_physical_schema, 
    read_neo4j_cypher,
    write_neo4j_cypher,
    reset_neo4j_data,
    create_uniqueness_constraint
)

from .prompts import instructions

AGENT_NAME = "cypher_agent_v1"
cypher_agent = Agent(
    name=AGENT_NAME,
    model=llm,
    description="Provides acccess to a Neo4j database through Cypher queries. Able to read/write data and answer configuration questions like the location of the import directory.", # Crucial for delegation later
    instruction=instructions[AGENT_NAME],

    tools=[neo4j_is_ready, 
        get_physical_schema, 
        read_neo4j_cypher, write_neo4j_cypher, 
        reset_neo4j_data,
        create_uniqueness_constraint,
        finished
        ], 
)

# Export the root agent so adk can find it
root_agent = cypher_agent
