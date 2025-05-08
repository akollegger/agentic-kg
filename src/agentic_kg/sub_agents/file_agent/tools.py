import os, shutil

import logging

from pathlib import Path
# import csv
import clevercsv
from itertools import islice

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

def get_state_value_or_else(key:str, error_message:str, tool_context:ToolContext) -> dict:
    """Gets a state value or else returns an error.
    Both the success and error values are returned as an ADK-friendly dict.
    """
    if key in tool_context.state:
        return {
            "status": "success",
            "value": tool_context.state[key]
        }
    else:
        return {
            "status": "error",
            "error_message": error_message
        }


def list_data_files(tool_context:ToolContext) -> dict:
    """Lists files available in the configured data directory
    that have gone through data preparation.

        Returns:
            dict: A dictionary containing metadata about the content.
                    Includes a 'status' key ('success' or 'error').
                    If 'success', includes a 'files' key with list of file names.
                    If 'error', includes an 'error_message' key.
    """
    data_dir_result = get_state_value_or_else("data_dir", "data_dir has not been configured, please check the .env",tool_context)
    if data_dir_result["status"] == "error": return data_dir_result
    data_dir = Path(data_dir_result["value"])

    file_names = [str(x) for x in data_dir.rglob("*") if x.is_file()]

    return {
        "status": "success",
        "files": file_names
    }

def list_import_files(tool_context:ToolContext) -> dict:
    """Lists files available in the configured Neo4j import directory
    that are ready for import by Neo4j.
    The import directory must be known before calling this tool.

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a 'files' key with list of file names.
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    import_dir_result = get_state_value_or_else("neo4j_import_dir", "Neo4j import directory not yet known.", tool_context)
    if import_dir_result["status"] == "error": return import_dir_result
    import_dir = Path(import_dir_result["value"])

    file_names = [str(x) for x in import_dir.rglob("*") if x.is_file()]

    return {
        "status": "success",
        "files": file_names
    }

def clear_import_dir(tool_context:ToolContext) -> dict:
    """Removes all files from the Neo4j import directory, leaving the directory itself in place.
    If the import directory is not known, first look it up using another tool.

    Returns:
        dict: A dictionary indicating the success of the operation, or an error.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'paths' key that has a list of removed paths.
              If 'error', includes an 'error_message' key.
              The 'error_message' may have instructions about how to handle the error.
    """
    import_dir_result = get_state_value_or_else("neo4j_import_dir", "Neo4j import directory not yet known.",tool_context)
    if import_dir_result["status"] == "error": return import_dir_result
    import_dir = Path(import_dir_result["value"])

    if not os.path.isdir(import_dir):
        return {
            "status":"error",
            "error_message": f"{import_dir} is not a directory."
        }
    sub_paths = [ f for f in import_dir.iterdir()]
    for sub_path in sub_paths:
        if sub_path.is_dir():
            shutil.rmtree(sub_path)
        else:
            os.remove(sub_path)
    return {
        "status": "success",
        "paths": [str(p.name) for p in sub_paths]
    }

def copy_file(source_path: str, destination_path: str, tool_context: ToolContext) -> dict:
    """Copies a file using the python shutil.copy2() method.

    Args:
      source_path: file to copy from.
      destination_path: destination to copy the file to.
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary indicating the success of the operation, or an error.
              The destination path will be returned as 'destination_path'
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """
    import shutil
    try:
        shutil.copy2(source_path, destination_path)
        return {
            "status": "success",
            "metadata": {
                "source_path": source_path,
                "destination_path": destination_path
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


def sample_file(path: str, size: int, tool_context: ToolContext) -> dict:
    """Retrieves a sample of file content that is enough for understanding
      what it contains.

    Args:
      path: file to fetch.
      size: either number of csv rows, or character count for text files.
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing metadata about the content,
              along with a sampling of the file.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """
    p = Path(path)
    if not (p.exists()):
        raise ValueError(f"Path does not exist: {path}")

    data = []
    with open(p, newline='') as csvfile:
        dialect = clevercsv.Sniffer().sniff(csvfile.read(2048))
        csvfile.seek(0)
        reader = clevercsv.reader(csvfile, dialect)
        data = list(islice(reader, size))

    result = {
        "status": "success",
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

    return result


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
        return {
            "status": "error",
            "error_message": "No samples have been taken."
        }

    if not sampled_path in tool_context.state["samples"]:
        return {
            "status": "error",
            "error_message": f"No sample found for {sampled_path}"
        }

    sample = tool_context.state["samples"][sampled_path]

    if not sample:
        return {
            "status": "error",
            "error_message": f"No sample available for {sampled_path}"
        }

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
        return {
            "status": "error",
            "error_message": "No samples have been taken."
        }

    if not sampled_path in tool_context.state["samples"]:
        return {
            "status": "error",
            "error_message": f"No sample found for {sampled_path}"
        }

    samples = tool_context.state["samples"]

    if not samples[sampled_path]:
        return {
            "status": "error",
            "error_message": f"No sample available for {sampled_path}"
        }
    
    samples[sampled_path]["annotations"].append(annotation)

    tool_context.state["samples"] = samples

    return samples[sampled_path]