from typing import Any, Optional, Dict, List

from google.adk.tools import ToolContext

from neo4j_graphrag.schema import get_structured_schema

from agentic_kg.neo4j_for_adk import (
    Neo4jForADK,
    is_write_query,
    tool_success, tool_error,
    ToolResult
)


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

async def reset_neo4j_data() -> ToolResult:
    """Removes all data, indexes and constraints from the
    Neo4j database. Use with caution! Confirm with the user
    that they know this will completely reset the database.

    Returns:
        Success or an error.
    """
    graphdb = Neo4jForADK.get_graphdb()
    # First, remove all nodes and relationships in batches
    data_removed = graphdb.send_query("""MATCH (n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 10000 ROWS""")
    if (data_removed["status"] == "error") :
        return data_removed

    # remove all constraints
    list_constraints = graphdb.send_query(
        """SHOW CONSTRAINTS YIELD name"""
    )
    if (list_constraints == "error"):
        return list_constraints
    constraint_names = [row["name"] for row in list_constraints["query_result"]]
    for constraint_name in constraint_names:
        dropped_constraint = graphdb.send_query("""DROP CONSTRAINT $constraint_name""", {"constraint_name": constraint_name})
        if (dropped_constraint["status"] == "error"):
            return dropped_constraint

    # remove all indexes
    list_indexes = graphdb.send_query(
        """SHOW INDEXES YIELD name"""
    )
    if (list_indexes == "error"):
        return list_indexes
    index_names = [row["name"] for row in list_indexes["query_result"]]
    for index_name in index_names:
        dropped_index = graphdb.send_query("""DROP INDEX $index_name""", {"index_name": index_name})
        if (dropped_index["status"] == "error"):
            return dropped_index

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
        tool_context.state["neo4j_import_dir"] = results["query_result"][0]["import_dir"]
    
    return results

