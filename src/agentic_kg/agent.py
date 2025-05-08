import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from google.adk.models.lite_llm import LiteLlm

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

from .prompts import instructions
from .sub_agents import cypher_agent, file_agent

import logging
logging.basicConfig(level=logging.ERROR)

from .neo4j_for_adk import Neo4jForADK
from .model_config import model_roles

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    print("API Keys Set:")
    print(f"Gemini API Key set: {'Yes' if os.environ.get('GEMINI_API_KEY') and os.environ['GEMINI_API_KEY'] != 'YOUR_GEMINI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
    print(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
    print(f"Anthropic API Key set: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

    # setting up model roles in session.state
    if "model_roles" not in callback_context.state:
        callback_context.state["model_roles"] = model_roles

    # setting up database settings in session.state
    if "neo4j_settings" not in callback_context.state:
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME") or "neo4j"
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        neo4j_database = os.getenv("NEO4J_DATABASE") or neo4j_username

        print("Neo4j expected at: " + f"{neo4j_username}@{neo4j_uri}/{neo4j_database}" )

        neo4j_settings = {
            "neo4j_uri": neo4j_uri,
            "neo4j_username": neo4j_username,
            "neo4j_password": neo4j_password,
            "neo4j_database": neo4j_database
        }
        callback_context.state["neo4j_settings"] = neo4j_settings

    Neo4jForADK.initialize(callback_context.state["neo4j_settings"])


def just_cypher_agent(): 
    return Agent(
        name="kg_agent_v1",
        model=LiteLlm(model=model_roles["chat"]),
        description="Knowledge graph construction using specialized sub-agents.", # Crucial for delegation later
        
        instruction=instructions["just_cypher_v1"],
        tools=[], # Make the tool available to this agent
        sub_agents=[cypher_agent],
        before_agent_callback=setup_before_agent_call,
    )

def cypher_and_files_agent():
    return Agent(
        name="kg_agent_v2",
        model=LiteLlm(model=model_roles["chat"]),
        description="Knowledge graph construction using specialized sub-agents.", # Crucial for delegation later
        
        instruction=instructions["cypher_and_files_v1"],
        tools=[], # Make the tool available to this agent
        sub_agents=[cypher_agent, file_agent],
        before_agent_callback=setup_before_agent_call,
    )

# Export the root agent so adk can find it
root_agent = cypher_and_files_agent()
