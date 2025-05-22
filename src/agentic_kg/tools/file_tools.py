import logging

from pathlib import Path
import clevercsv
from itertools import islice

from google.adk.tools import ToolContext
from typing import Dict, Any

from agentic_kg.common.neo4j_for_adk import graphdb
from agentic_kg.common.util import tool_success, tool_error

logger = logging.getLogger(__name__)


def get_neo4j_import_directory(tool_context:ToolContext) -> Dict[str, Any]:
    """Queries Neo4j to find the location of the server's import directory,
       which is where files need to be located in order to be used by LOAD CSV.
    """
    if "neo4j_import_dir" in tool_context.state:
        return tool_success("neo4j_import_dir",tool_context.state["neo4j_import_dir"])
        
    results = graphdb.get_import_directory() # use the helper available in Neo4jForADK
    
    if results["status"] == "success":
        tool_context.state["neo4j_import_dir"] = results["neo4j_import_dir"]
    return results

def list_import_files(tool_context:ToolContext) -> dict:
    """Lists files available in the configured Neo4j import directory
    that are ready for import by Neo4j.

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a 'files' key with list of file names.
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    import_dir_result = get_neo4j_import_directory(tool_context) # chain tool call
    if import_dir_result["status"] == "error": return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])

    file_names = [str(x.relative_to(import_dir)) for x in import_dir.rglob("*") if x.is_file()]

    return tool_success("files", file_names)


def sample_file(path: str, size: int, tool_context: ToolContext) -> dict:
    """Retrieves a sample of file content that is enough for understanding
      what it contains.

    Args:
      path: file to sample, relative to the import directory
      size: either number of csv rows, or character count for text files.
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing metadata about the content,
              along with a sampling of the file.
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

    data = []
    with open(p, newline='') as csvfile:
        dialect = clevercsv.Sniffer().sniff(csvfile.read(2048))
        csvfile.seek(0)
        reader = clevercsv.reader(csvfile, dialect)
        data = list(islice(reader, size))

    result = {
        "metadata": {
            "path": path,
            "mimetype": "text/csv"
        },
        "data": data,
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