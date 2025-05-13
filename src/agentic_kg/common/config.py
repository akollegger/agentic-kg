import os 
from openai import OpenAI

from agentic_kg.common.neo4j_for_adk import Neo4jForADK

MODEL_GEMINI_2_0_FLASH = "gemini/gemini-2.0-flash"
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"
MODEL_OPENAI_CHAT = "openai/gpt-4o"
MODEL_GPT_40_MINI = "openai/gpt-4o-mini"

model_roles = {
    "chat": MODEL_GPT_40_MINI,
    "embed": MODEL_GEMINI_2_0_FLASH,
    "code": MODEL_CLAUDE_SONNET
}

def load_and_connect():
    """Load environmental configuration and establish connection to Neo4j."""

    # Configure and  OpenAI
    print(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="You are a terse but friendly assistant.",
        input="Hello OpenAI!",
    )
    print("OpenAI says: ", response.output_text)


    # Configure and set up Neo4j
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_username = os.getenv("NEO4J_USERNAME") or "neo4j"
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE") or neo4j_username

    print("Neo4j expected at: " + f"{neo4j_username}@{neo4j_uri}/{neo4j_database}" )

    Neo4jForADK.initialize({
        "neo4j_uri": neo4j_uri,
        "neo4j_username": neo4j_username,
        "neo4j_password": neo4j_password,
        "neo4j_database": neo4j_database
    })

