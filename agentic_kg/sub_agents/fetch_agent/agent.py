from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

import logging
import urllib.request

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

from agentic_kg.model_config import model_roles

from .tools import list_files, read_file

fetch_agent = Agent(
    name="fetch_agent_v1",
    model=LiteLlm(model=model_roles["chat"]),
    description="Manages reading local files and providing metadata about them.", # Crucial for delegation later
    instruction="""You are a helpful file manager. Your primary goal is to read files, understand their content,
                and make the content available for further processing.

                When the user asks to load a particular file
                you MUST use the 'read_file' tool to load it from the local filesystem.
                Analyze the tool's response: if the status is 'error', inform the user politely about the error message.
                If the status is 'success', present the 'metadata' about the file clearly and concisely to the user.
                """,
    tools=[list_files, read_file], # Make the tool available to this agent
)

# Export the root agent so adk can find it
root_agent = fetch_agent
