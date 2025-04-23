import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from google.adk.models.lite_llm import LiteLlm

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

from .prompts import return_instructions_root
from .sub_agents import weather_agent, cypher_agent

import logging
logging.basicConfig(level=logging.ERROR)

from dotenv import load_dotenv
load_dotenv()

from .model_config import model_roles

print("API Keys Set:")
print(f"Gemini API Key set: {'Yes' if os.environ.get('GEMINI_API_KEY') and os.environ['GEMINI_API_KEY'] != 'YOUR_GEMINI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"Anthropic API Key set: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

print("\nEnvironment configured.")

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up model roles in session.state
    if "model_roles" not in callback_context.state:
        callback_context.state["model_roles"] = model_roles


experimental_agent = Agent(
    name="experimental_agent_v1",
    model=LiteLlm(model=model_roles["chat"]),
    description="General purpose chatting, tool use, and delegation to sub-agents.", # Crucial for delegation later
    
    instruction=return_instructions_root(),
    tools=[], # Make the tool available to this agent
    sub_agents=[weather_agent, cypher_agent],
    before_agent_callback=setup_before_agent_call,
)

# Export the root agent so adk can find it
root_agent = experimental_agent
