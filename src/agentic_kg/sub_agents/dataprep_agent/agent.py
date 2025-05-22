from google.adk.agents import Agent

import logging

from agentic_kg.tools import get_user_goal, finished

logger = logging.getLogger(__name__)

from agentic_kg.common.config import llm

from .prompts import instructions
from agentic_kg.tools.file_tools import list_import_files, sample_file

AGENT_NAME = "dataprep_agent_v2"
dataprep_agent = Agent(
    name=AGENT_NAME,
    model=llm,
    description="Manages reading files and providing metadata about them.",
    instruction=instructions[AGENT_NAME],
    tools=[
        get_user_goal, list_import_files, sample_file, finished
    ], 
)

# Export the root agent so adk can find it
root_agent = dataprep_agent
