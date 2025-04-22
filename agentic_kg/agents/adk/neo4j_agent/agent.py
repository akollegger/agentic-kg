import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from graph_intelligence.tools.neo4j.neo4j_interaction import prepare_interaction

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

from dotenv import load_dotenv
load_dotenv()

print("API Keys Set:")
print(f"Gemini API Key set: {'Yes' if os.environ.get('GEMINI_API_KEY') and os.environ['GEMINI_API_KEY'] != 'YOUR_GEMINI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"Anthropic API Key set: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

# Note: Specific model names might change. Refer to LiteLLM or the model provider's documentation.
MODEL_GEMINI_2_0_FLASH = "gemini/gemini-2.0-flash"
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"

_driver = GraphDatabase.driver(
    neo4j_uri,
    auth=(neo4j_username, neo4j_password)
)

# Prepare a cypher interaction environment
interact = prepare_interaction(
    _driver,
    "neo4j"
)


def query_neo4j(cypher: str) -> dict:
    """Execute a read Cypher query on the neo4j database.

    Args:
        cypher (str): The Cypher query to execute.

    Returns:
        dict: A dictionary containing results from the graph database.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'results' key with weather details.
              If 'error', includes an 'error_message' key.
    """

    # if _is_write_query(query):
    #     raise ValueError("Only MATCH queries are allowed for read-query")

    result = interact(cypher)
    return {}
    


neo4j_agent = Agent(
    name="neo4j_agent_v1",
    model=LiteLlm(model=MODEL_GEMINI_2_0_FLASH),
    description="Provides weather information for specific cities.", # Crucial for delegation later
    instruction="You are a helpful weather assistant. Your primary goal is to provide current weather reports. "
                "When the user asks for the weather in a specific city, "
                "you MUST use the 'get_weather' tool to find the information. "
                "Analyze the tool's response: if the status is 'error', inform the user politely about the error message. "
                "If the status is 'success', present the weather 'report' clearly and concisely to the user. "
                "Only use the tool when a city is mentioned for a weather request.",
    tools=[get_weather], # Make the tool available to this agent
)

# Export the root agent so adk can find it
root_agent = weather_agent
