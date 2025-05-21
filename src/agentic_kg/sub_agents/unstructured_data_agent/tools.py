import os, shutil

import logging

from pathlib import Path
# import csv
import clevercsv
from itertools import islice

from google.adk.tools import ToolContext
from typing import Dict, Any

from agentic_kg.common.neo4j_for_adk import graphdb
from agentic_kg.common.util import tool_success, tool_error

logger = logging.getLogger(__name__)


def sample_markdown_file(path: str, tool_context: ToolContext) -> dict:
    """Reads the content of a markdown file.

    Args:
      path: file to read, relative to the import directory
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing metadata about the file,
              along with the file content.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """
    import_dir_result = get_neo4j_import_directory(tool_context) # chain tool call
    if import_dir_result["status"] == "error": return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    p = import_dir / path
    if not (p.exists()):
        return tool_error(f"Path does not exist: {path}")

    text = ""
    with open(p, 'r') as mdfile:
        text = mdfile.read()

    result = {
        "metadata": {
            "path": path,
            "mimetype": "text/markdown"
        },
        "text": text,
        "annotations": []
    }

    if not "samples" in tool_context.state:
        tool_context.state["samples"] = {}

    tool_context.state["samples"][str(p)] = result

    return tool_success("samples", result)


def show_sample(path: str, tool_context: ToolContext) -> dict:
    """Shows the sample taken from a sample of file along with any
        recorded annotations.

    Args:
      path: file to fetch.
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing metadata about the content,
              along with a sampling of the file.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """
    if not "samples" in tool_context.state:
        return tool_error("No samples have been taken.")

    if not sampled_path in tool_context.state["samples"]:
        return tool_error(f"No sample found for {sampled_path}")

    sample = tool_context.state["samples"][sampled_path]

    if not sample:
        return tool_error(f"No sample available for {sampled_path}")

    return sample

def annotate_sample(sampled_path: str, annotation: str, tool_context: ToolContext) -> dict:
    """Annotates a sampled file to provide descriptive information.

    Args:
      sampled_path: previously sampled file.
      annotation: information to annotate on the sample.
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing metadata about the content,
              along with a sampling of the file.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """
    
    if not "samples" in tool_context.state:
        return tool_error("No samples have been taken.")

    if not sampled_path in tool_context.state["samples"]:
        return tool_error(f"No sample found for {sampled_path}")

    samples = tool_context.state["samples"]

    if not samples[sampled_path]:
        return tool_error(f"No sample available for {sampled_path}")
    
    samples[sampled_path]["annotations"].append(annotation)

    tool_context.state["samples"] = samples

    return samples[sampled_path]