import os 
from openai import OpenAI

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

def load_neo4j_env():
    return {
        "neo4j_uri": os.getenv("NEO4J_URI"),
        "neo4j_username": os.getenv("NEO4J_USERNAME") or "neo4j",
        "neo4j_password": os.getenv("NEO4J_PASSWORD"),
        "neo4j_database": os.getenv("NEO4J_DATABASE") or os.getenv("NEO4J_USERNAME") or "neo4j"
    }

def validate_env():
    """Load environmental configuration and establish connection to Neo4j."""

    # Validate OpenAI settings
    valid_openai_api_key = os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY'
    print(f"OpenAI API Key set: {'Yes' if valid_openai_api_key else 'No (REPLACE PLACEHOLDER!)'}")
    if not valid_openai_api_key:
        raise ValueError("OpenAI API Key not set or placeholder not replaced.")


    # Validate Neo4j settings
    neo4j_settings = load_neo4j_env()
    print("Neo4j expected at: " + f"{neo4j_settings['neo4j_username']}@{neo4j_settings['neo4j_uri']}/{neo4j_settings['neo4j_database']}" )

    if not neo4j_settings['neo4j_uri'] or not neo4j_settings['neo4j_password']:
        raise ValueError("Neo4j URI or password not set.")


