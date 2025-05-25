import logging

from pathlib import Path
import clevercsv
from itertools import islice

from google.adk.tools import ToolContext
from typing import Dict, Any, List

from agentic_kg.common.neo4j_for_adk import graphdb
from agentic_kg.common.util import tool_success, tool_error

logger = logging.getLogger(__name__)

CURRENT_FILES = "current_file_list"
SUGGESTED_FILES = "suggested_file_list"
ACCEPTED_FILES = "accepted_file_list"

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
    f"""Lists files available in the configured Neo4j import directory
    that are ready for import by Neo4j.

    Saves the list to {CURRENT_FILES} in state.

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

    # Filter for supported file extensions
    supported_extensions = {'.csv', '.md', '.txt'}
    file_names = [str(x.relative_to(import_dir)) 
                 for x in import_dir.rglob("*") 
                 if x.is_file() and x.suffix.lower() in supported_extensions]

    tool_context.state[CURRENT_FILES] = file_names

    return tool_success("files", file_names)

def set_suggested_files(suggest_files:List[str]) -> Dict[str, Any]:
    tool_context.state[SUGGESTED_FILES] = suggest_files
    return tool_success("suggested_files", suggest_files)

def accept_suggested_file_list(tool_context:ToolContext) -> Dict[str, Any]:
    f"""Accepts the {SUGGESTED_FILES} in state for further processing."""
    
    if SUGGESTED_FILES not in tool_context.state:
        return tool_error("Current files have not been set. Take no action other than to inform user.")

    tool_context.state[ACCEPTED_FILES] = tool_context.state[SUGGESTED_FILES]


def sample_csv_file(path: str, size: int, tool_context: ToolContext) -> dict:
    """Retrieves a sample of a csv file content that is enough for understanding
      what it contains.

    Args:
      path: file to sample, relative to the import directory
      size: number of csv rows to sample.
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

import re
import yaml

def sample_markdown_file(file_path: str, tool_context: ToolContext):
    """Reads the content of a markdown file.

    Args:
      file_path: file to sample, relative to the import directory
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
    p = import_dir / file_path
    if not (p.exists()):
        return tool_error(f"Path does not exist: {file_path}")

    content = ""

    try:
        with open(p, 'r', encoding='utf-8') as mdfile:
            full_text = mdfile.read()

        content = full_text

    except Exception as e:
        return tool_error(f"Error reading or processing markdown file {file_path}: {e}")

    result = {
        "metadata": {
            "path": file_path,
            "mimetype": "text/markdown"
        },
        "content": content,
        "annotations": []
    }

    if not "samples" in tool_context.state:
        tool_context.state["samples"] = {}

    tool_context.state["samples"][str(p)] = result

    return tool_success("samples", result)


def search_csv_file(file_path: str, query: str, tool_context: ToolContext, case_sensitive: bool = False) -> dict:
    """
    Searches a CSV file for rows containing the given query string in any of its fields.

    Args:
      file_path: Path to the CSV file, relative to the Neo4j import directory.
      query: The string to search for.
      tool_context: The ToolContext object.
      case_sensitive: Whether the search should be case-sensitive (default: False).

    Returns:
        dict: A dictionary with 'status' ('success' or 'error').
              If 'success', includes 'search_results' containing 'matching_rows'
              (a list of rows, where each row is a list of strings)
              and 'metadata' (path, mimetype, query, case_sensitive, rows_found).
              If 'error', includes an 'error_message'.
    """
    import_dir_result = get_neo4j_import_directory(tool_context)
    if import_dir_result["status"] == "error":
        return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    p = import_dir / file_path

    if not p.exists():
        return tool_error(f"CSV file does not exist: {file_path}")
    if not p.is_file():
        return tool_error(f"Path is not a file: {file_path}")
    if not (p.suffix.lower() == ".csv"):
        # Basic check, could be enhanced with mimetypes for more accuracy
        logger.warning(f"File {file_path} does not have a .csv extension, but attempting to process as CSV.")

    matching_rows = []
    search_query = query if case_sensitive else query.lower()
    header_row = []

    try:
        # Handle empty query - return no results
        if not query:
            with open(p, 'r', newline='', encoding='utf-8') as csvfile:
                try:
                    # Just read enough to get the header
                    dialect = clevercsv.Sniffer().sniff(csvfile.read(2048))
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile, dialect)
                except clevercsv.Error:
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile)
                header_row = next(reader, [])
                # Empty query returns no matches, but we still read the header
        else:
            with open(p, 'r', newline='', encoding='utf-8') as csvfile:
                try:
                    # Read a chunk to sniff dialect, then rewind
                    dialect = clevercsv.Sniffer().sniff(csvfile.read(2048))
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile, dialect)
                except clevercsv.Error:
                    # Fallback if sniffing fails (e.g., empty or very small file, or not CSV)
                    csvfile.seek(0)
                    reader = clevercsv.reader(csvfile) # Use default dialect
                    logger.warning(f"Could not sniff CSV dialect for {file_path}. Using default dialect.")
                
                header_row = next(reader, []) # Store header, or empty list if file is empty
                
                for row in reader:
                    for field in row:
                        field_to_check = str(field) if case_sensitive else str(field).lower()
                        if search_query in field_to_check:
                            matching_rows.append(row)
                            break # Move to next row once a match is found
    except Exception as e:
        return tool_error(f"Error reading or searching CSV file {file_path}: {e}")

    result_data = {
        "metadata": {
            "path": file_path,
            "mimetype": "text/csv",
            "query": query,
            "case_sensitive": case_sensitive,
            "header": header_row,
            "rows_found": len(matching_rows)
        },
        "matching_rows": matching_rows
    }
    return tool_success("search_results", result_data)


def show_sample(path: str, tool_context: ToolContext) -> dict:
    """Shows the sample taken from a file along with any recorded annotations.

    Args:
      path: file to fetch, relative to the import directory.
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing the sample data.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes 'retrieved_sample' with the sample details.
              If 'error', includes an 'error_message' key.
    """
    import_dir_result = get_neo4j_import_directory(tool_context)
    if import_dir_result["status"] == "error":
        return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    
    absolute_path_str = str(import_dir / path)

    if "samples" not in tool_context.state:
        return tool_error("No samples have been taken yet.")

    if absolute_path_str not in tool_context.state["samples"]:
        return tool_error(f"No sample found for path: {path}")

    sample_data = tool_context.state["samples"][absolute_path_str]
    
    # Return the sample data
    return tool_success("retrieved_sample", sample_data)


def search_file(file_path: str, query: str, tool_context: ToolContext) -> dict:
    """
    Searches any text file (markdown, csv, txt)for lines containing the given query string.
    Simple grep-like functionality that works with any text file.
    Search is always case insensitive.

    Args:
      file_path: Path to the file, relative to the Neo4j import directory.
      query: The string to search for.
      tool_context: The ToolContext object.

    Returns:
        dict: A dictionary with 'status' ('success' or 'error').
              If 'success', includes 'search_results' containing 'matching_lines'
              (a list of dictionaries with 'line_number' and 'content' keys)
              and basic metadata about the search.
              If 'error', includes an 'error_message'.
    """
    import_dir_result = get_neo4j_import_directory(tool_context)
    if import_dir_result["status"] == "error":
        return import_dir_result
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    p = import_dir / file_path

    if not p.exists():
        return tool_error(f"File does not exist: {file_path}")
    if not p.is_file():
        return tool_error(f"Path is not a file: {file_path}")

    # Check if file has an acceptable extension
    file_ext = p.suffix.lower()
    supported_extensions = {".csv", ".md", ".txt"}
    if file_ext not in supported_extensions:
        logger.warning(f"File {file_path} has an unsupported extension {file_ext}, but attempting to search anyway.")

    # Handle empty query - return no results
    if not query:
        return tool_success("search_results", {
            "metadata": {
                "path": file_path,
                "query": query,
                "lines_found": 0
            },
            "matching_lines": []
        })

    matching_lines = []
    search_query = query.lower()
    
    try:
        with open(p, 'r', encoding='utf-8') as file:
            # Process the file line by line
            for i, line in enumerate(file, 1):
                line_to_check = line.lower()
                if search_query in line_to_check:
                    matching_lines.append({
                        "line_number": i,
                        "content": line.strip()  # Remove trailing newlines
                    })
                        
    except Exception as e:
        return tool_error(f"Error reading or searching file {file_path}: {e}")

    # Prepare basic metadata
    metadata = {
        "path": file_path,
        "query": query,
        "lines_found": len(matching_lines)
    }
    
    result_data = {
        "metadata": metadata,
        "matching_lines": matching_lines
    }
    return tool_success("search_results", result_data)

async def import_markdown_file(source_file: str, label_name: str, tool_context: ToolContext):
    """Reads the content of a markdown file then creates a text node in Neo4j.
    The node will only have two properties:
    - content: the entire content of the markdown file

    Args:
      source_file: path to the markdown file, relative to the import directory
      label_name: the label applied to the created node
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary indicating success or failure.
              Includes a 'status' key ('success' or 'error').
              If 'error', includes an 'error_message' key.
    """
    from agentic_kg.sub_agents.cypher_agent.tools import create_uniqueness_constraint, write_neo4j_cypher
    
    # 1. Ensure that a property constraint has been created for label/source_file
    constraint_result = await create_uniqueness_constraint(label_name, "source_file")
    if constraint_result["status"] == "error":
        return constraint_result
    
    # 2. Read the content of the markdown
    import_dir_result = get_neo4j_import_directory(tool_context)
    if import_dir_result["status"] == "error":
        return import_dir_result
    
    import_dir = Path(import_dir_result["neo4j_import_dir"])
    file_path = import_dir / source_file
    
    if not file_path.exists():
        return tool_error(f"Markdown file does not exist: {source_file}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as mdfile:
            content = mdfile.read()
    except Exception as e:
        return tool_error(f"Error reading markdown file {source_file}: {e}")
    
    # 3. Create a node for the markdown using a parameterized cypher query
    query = "MERGE (t:$($label_name) {source_file: $source_file}) SET t.content = $content"
    properties = {
        "label_name": label_name,
        "source_file": source_file,
        "content": content
    }
    return await write_neo4j_cypher(query, properties)
    