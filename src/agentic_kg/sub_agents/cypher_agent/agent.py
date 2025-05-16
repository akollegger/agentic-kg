from google.adk.agents import Agent

from google.adk.models.lite_llm import LiteLlm

from agentic_kg.common.config import model_roles

from .tools import (
    neo4j_is_ready, 
    get_physical_schema, 
    read_neo4j_cypher,
    write_neo4j_cypher,
    reset_neo4j_data,
    create_uniqueness_constraint
)

from .prompts import return_instructions_cypher


# Export the root agent so adk can find it
cypher_agent = Agent(
    name="cypher_agent_v1",
    model=LiteLlm(model=model_roles["chat"]),
    description="Provides acccess to a Neo4j database through Cypher queries. Able to read/write data, create indexes and constraints.", 
    instruction=return_instructions_cypher(),

    tools=[neo4j_is_ready, 
        get_physical_schema, 
        read_neo4j_cypher, write_neo4j_cypher, 
        reset_neo4j_data,
        create_uniqueness_constraint
        ], 
)

# Export the root agent so adk can find it
root_agent = cypher_agent
