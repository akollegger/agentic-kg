
import logging

from pathlib import Path
import csv
from itertools import islice

from google.adk.tools import ToolContext


from typing import Any, Optional, Dict, List

from google.adk.tools import ToolContext

from neo4j_graphrag.schema import get_structured_schema

from agentic_kg.neo4j_for_adk import (
    Neo4jForADK,
    is_write_query,
    tool_success, tool_error,
    ToolResult
)

logger = logging.getLogger(__name__)

async def create_note(reference:str, title:str, text: str, tool_context: ToolContext) -> dict:
    """Saves a note for later  reference.

    Args:
      reference: an identifier referrring to the subject of this note, like a filename or path
      title: brief title indicating the intent of the note
      text: the body of the note
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing metadata about the content,
              along with a sampling of the file.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """

    graphdb = Neo4jForADK.get_graphdb()
    results = graphdb.send_query("CREATE (:Note {title: $title, text: $text})",
        parameters={
            "title": title,
            "text": text
        }
    )
    print(results)
    return results


async def get_neo4j_import_directory(tool_context:ToolContext) -> dict:
    """Queries Neo4j to find the location of the server's import directory,
       which is where files need to be located in order to be used by LOAD CSV.
    """
    find_neo4j_data_dir_cypher = """
    Call dbms.listConfig() YIELD name, value
    WHERE name CONTAINS 'server.directories.import'
    RETURN value as import_dir
    """
    graphdb = Neo4jForADK.get_graphdb()

    results = graphdb.send_query(find_neo4j_data_dir_cypher)

    if results["status"] == "success":
        tool_context.state["neo4j_settings"]["import_dir"] = results["query_result"][0]["import_dir"]
    
    return results

