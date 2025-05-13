import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from google.adk.models.lite_llm import LiteLlm

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

from agentic_kg.sub_agents import cypher_agent, file_agent
from agentic_kg.common.config import model_roles

from .prompts import instructions

cypher_and_files_agent = Agent(
        name="kg_agent_v2",
        model=LiteLlm(model=model_roles["chat"]),
        description="Knowledge graph construction using specialized sub-agents.", # Crucial for delegation later
        
        instruction=instructions["cypher_and_files_v1"],
        tools=[], # Make the tool available to this agent
        sub_agents=[cypher_agent, file_agent],
    )

# Export the root agent so adk can find it
root_agent = cypher_and_files_agent
