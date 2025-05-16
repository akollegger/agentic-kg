import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm

import logging

logger = logging.getLogger(__name__)

from agentic_kg.common.config import llm

from .prompts import return_instructions
from .tools import list_data_files, list_import_files, copy_to_import_dir, sample_file, annotate_sample, clear_import_dir

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    data_dir = os.getenv("DATA_DIR") or "data"
    data_dir_path = Path(data_dir).absolute()

    print(f"Import directory from environment: {data_dir}")
    print(f"Import directory set (absolute): {data_dir_path}")

    if not (data_dir_path.exists() and data_dir_path.is_dir()):
        raise ValueError(f"DATA_DIR missing or not a directory: {data_dir}")

    callback_context.state["data_dir"] = str(data_dir_path)


dataprep_agent = Agent(
    name="dataprep_agent_v1",
    model=llm,
    description="Manages reading local files and providing metadata about them.", # Crucial for delegation later
    instruction=return_instructions(),
    tools=[
        list_data_files, list_import_files, copy_to_import_dir, sample_file, clear_import_dir, annotate_sample
    ], 
    before_agent_callback=setup_before_agent_call,
)

# Export the root agent so adk can find it
root_agent = dataprep_agent
