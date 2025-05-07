import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm

import logging
import urllib.request

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

from agentic_kg.model_config import model_roles

from .tools import list_data_files, list_import_files, copy_file, sample_file, annotate_sample, clear_import_dir
from .kg_tools import get_neo4j_import_directory, create_note

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    data_dir = os.getenv("DATA_DIR") or "data"
    data_dir_path = Path(data_dir).absolute()

    print(f"Import directory from environment: {data_dir}")
    print(f"Import directory set (absolute): {data_dir_path}")

    if not (data_dir_path.exists() and data_dir_path.is_dir()):
        raise ValueError(f"DATA_DIR missing or not a directory: {data_dir}")

    callback_context.state["data_dir"] = str(data_dir_path)


file_agent = Agent(
    name="file_agent_v1",
    model=LiteLlm(model=model_roles["chat"]),
    description="Manages reading local files and providing metadata about them.", # Crucial for delegation later
    instruction="""You are a helpful file manager. Your primary goal is to read files
                and understand their content.

                You have access to two data directories:

                1. data_dir has files that have gone through data preparation
                2. import_dir has files that Neo4j is able to directly access

                When the user asks about a particular file
                you MUST use the 'sample_file' tool to load part of it from the local filesystem.
                Analyze the tool's response: if the status is 'error', inform the user politely about the error message.
                If the status is 'success', present the 'metadata' about the file clearly and concisely to the user.
                """,
    tools=[list_data_files, list_import_files, copy_file, get_neo4j_import_directory, sample_file, clear_import_dir, annotate_sample, create_note], # Make the tool available to this agent
    before_agent_callback=setup_before_agent_call,
)

# Export the root agent so adk can find it
root_agent = file_agent
