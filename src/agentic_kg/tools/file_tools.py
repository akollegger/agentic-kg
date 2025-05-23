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

    # Filter for supported file extensions
    supported_extensions = {'.csv', '.md', '.txt'}
    file_names = [str(x.relative_to(import_dir)) 
                 for x in import_dir.rglob("*") 
                 if x.is_file() and x.suffix.lower() in supported_extensions]

    return tool_success("files", file_names)


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
    """Reads the content of a markdown file, parsing optional YAML frontmatter.

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

    frontmatter = {}
    content = ""

    try:
        with open(p, 'r', encoding='utf-8') as mdfile:
            full_text = mdfile.read()

        # Regex to find YAML frontmatter (---...---)
        # It must be at the very beginning of the file.
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', full_text, re.DOTALL | re.MULTILINE)

        if fm_match:
            fm_string = fm_match.group(1)
            content = fm_match.group(2).strip()
            try:
                frontmatter = yaml.safe_load(fm_string)
                if not isinstance(frontmatter, dict):
                    # If YAML is valid but not a dict (e.g. a list or a string), treat as no frontmatter
                    logger.warning(f"Frontmatter in {file_path} is not a dictionary. Treating as plain content.")
                    frontmatter = {}
                    content = full_text # Revert to full text if frontmatter is not a dict
            except yaml.YAMLError as e:
                logger.warning(f"Could not parse YAML frontmatter in {file_path}: {e}. Treating as plain content.")
                # If YAML is invalid, treat the whole thing as content
                content = full_text
        else:
            content = full_text

    except Exception as e:
        return tool_error(f"Error reading or processing markdown file {file_path}: {e}")

    result = {
        "metadata": {
            "path": file_path,
            "mimetype": "text/markdown"
        },
        "frontmatter": frontmatter,
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


# Keep these functions for backward compatibility, but implement them using search_file
def search_markdown_file(file_path: str, query: str, tool_context: ToolContext, case_sensitive: bool = False) -> dict:
    """
    Searches a Markdown file for lines containing the given query string.
    This is a wrapper around search_file for backward compatibility.
    Note: case_sensitive parameter is ignored, search is always case insensitive.

    Args:
      file_path: Path to the Markdown file, relative to the Neo4j import directory.
      query: The string to search for.
      tool_context: The ToolContext object.
      case_sensitive: Whether the search should be case-sensitive (ignored).

    Returns:
        dict: See search_file for details.
    """
    return search_file(file_path, query, tool_context)


def search_csv_file(file_path: str, query: str, tool_context: ToolContext, case_sensitive: bool = False) -> dict:
    """
    Searches a CSV file for rows containing the given query string.
    This is a wrapper around search_file for backward compatibility.
    Note: case_sensitive parameter is ignored, search is always case insensitive.

    Args:
      file_path: Path to the CSV file, relative to the Neo4j import directory.
      query: The string to search for.
      tool_context: The ToolContext object.
      case_sensitive: Whether the search should be case-sensitive (ignored).

    Returns:
        dict: See search_file for details.
    """
    return search_file(file_path, query, tool_context)


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

    sample = tool_context.state["samples"][sampled_path]

    if not sample:
        return tool_error(f"No sample available for {sampled_path}")

    if not "annotations" in sample:
        sample["annotations"] = []

    sample["annotations"].append(annotation)

    return tool_success("annotations", sample["annotations"])