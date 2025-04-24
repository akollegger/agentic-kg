
from typing import Any, Optional, Dict, List

from google.adk.tools import ToolContext

from neo4j_graphrag.schema import get_structured_schema

from agentic_kg.neo4j_for_adk import (
    Neo4jForADK,
    is_write_query,
    tool_success, tool_error,
    ToolResult
)

def ensure_neo4j_settings(tool_context: ToolContext) -> bool:
    if "neo4j_settings" not in tool_context.state:
        return False
    return True


async def neo4j_is_ready(
):
    """Tool to check that the Neo4j database is ready.
    Replies with either a positive message about the database being ready or an error message.
    """
    graphdb = Neo4jForADK.get_graphdb()
    results = graphdb.send_query("RETURN 'Neo4j is Ready!' as message")
    return results


async def get_physical_schema(
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Tool to get the physical schema of a Neo4j graph database.

    The schema is returned as a JSON object containing a description
    of the node labels and relationship types.
    """
    neo4j_database = tool_context.state["neo4j_settings"]["neo4j_database"]
    graphdb = Neo4jForADK.get_graphdb()
    driver = graphdb.get_driver()
    
    try:
        schema = get_structured_schema(driver, database=neo4j_database)
        return tool_success(schema)
    except Exception as e:
        return tool_error(str(e))


async def read_neo4j_cypher(
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """Submits a Cypher query to read from a Neo4j database.

    Args:
        query: The Cypher query string to execute.
        params: Optional parameters to pass to the query.

    Returns:
        A list of dictionaries containing the results of the query.
        Returns an empty list "[]" if no results are found.

    """    
    if is_write_query(query):
        return tool_error("Only MATCH queries are allowed for read-query")

    graphdb = Neo4jForADK.get_graphdb()
    results = graphdb.send_query(query, params)
    return results

async def write_neo4j_cypher(
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """Submits a Cypher query to write to a Neo4j database.
    Make sure you have permission to write before calling this.

    Args:
        query: The Cypher query string to execute.
        params: Optional parameters to pass to the query.

    Returns:
        A list of dictionaries containing the results of the query.
        Returns an empty list "[]" if no results are found.
    """
    graphdb = Neo4jForADK.get_graphdb()
    results = graphdb.send_query(query, params)
    return results