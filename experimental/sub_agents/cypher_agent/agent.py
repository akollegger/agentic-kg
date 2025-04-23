from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from google.adk.models.lite_llm import LiteLlm

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import os

from experimental.model_config import model_roles

from .tools import neo4j_is_ready, get_physical_schema, read_neo4j_cypher
from .prompts import return_instructions_cypher

def prepare_neo4j() -> dict:

    # Load environment variables and set up driver configuration    
    from dotenv import load_dotenv
    load_dotenv()
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE") or "neo4j"

    return {
        "neo4j_uri": neo4j_uri,
        "neo4j_username": neo4j_username,
        "neo4j_password": neo4j_password,
        "neo4j_database": neo4j_database
    }

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "neo4j_settings" not in callback_context.state:
        callback_context.state["neo4j_settings"] = prepare_neo4j()

# Export the root agent so adk can find it
cypher_agent = Agent(
    name="cypher_agent_v1",
    model=LiteLlm(model=model_roles["chat"]),
    description="Provides acccess to a Neo4j database through Cypher queries.", # Crucial for delegation later
    instruction=return_instructions_cypher(),

    tools=[neo4j_is_ready, get_physical_schema, read_neo4j_cypher], # Make the tool available to this agent
    before_agent_callback=setup_before_agent_call,
)

# Export the root agent so adk can find it
root_agent = cypher_agent
