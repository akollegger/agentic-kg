import os

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm

import logging
import urllib.request

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

from agentic_kg.model_config import model_roles

from .tools import list_files, copy_file, sample_file, annotate_sample
from .kg_tools import get_neo4j_import_directory, create_note

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    import_dir = os.getenv("IMPORT_DIR") or "data"
    import_dir_path = Path(import_dir).absolute()

    print(f"Import directory from environment: {import_dir}")
    print(f"Import directory set (absolute): {import_dir_path}")

    if not (import_dir_path.exists() and import_dir_path.is_dir()):
        raise ValueError(f"IMPORT_DIR missing or not a directory: {import_dir}")

    callback_context.state["import_dir"] = str(import_dir_path)


file_agent = Agent(
    name="file_agent_v1",
    model=LiteLlm(model=model_roles["chat"]),
    description="Manages reading local files and providing metadata about them.", # Crucial for delegation later
    instruction="""You are a helpful file manager. Your primary goal is to read files
                and understand their content.

                When the user asks about a particular file
                you MUST use the 'sample_file' tool to load part of it from the local filesystem.
                Analyze the tool's response: if the status is 'error', inform the user politely about the error message.
                If the status is 'success', present the 'metadata' about the file clearly and concisely to the user.
                """,
    tools=[list_files, copy_file, get_neo4j_import_directory, sample_file, annotate_sample, create_note], # Make the tool available to this agent
    before_agent_callback=setup_before_agent_call,
)

# Export the root agent so adk can find it
root_agent = file_agent
