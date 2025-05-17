import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm

import logging

logger = logging.getLogger(__name__)

from agentic_kg.common.config import llm

from .prompts import return_instructions
from .tools import list_import_files, sample_file

dataprep_agent = Agent(
    name="dataprep_agent_v1",
    model=llm,
    description="Manages reading files and providing metadata about them.",
    instruction=return_instructions(),
    tools=[
        list_import_files, sample_file
    ], 
)

# Export the root agent so adk can find it
root_agent = dataprep_agent
