from typing import Any, Optional, Dict, List

from google.adk.tools import ToolContext

from neo4j_graphrag.schema import get_structured_schema

from agentic_kg.common.neo4j_for_adk import (
    graphdb,
    is_write_query,
    tool_success, tool_error
)


async def neo4j_is_ready(
):
    """Tool to check that the Neo4j database is ready.
    Replies with either a positive message about the database being ready or an error message.
    """
    results = graphdb.send_query("RETURN 'Neo4j is Ready!' as message")
    return results


async def get_physical_schema(
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Tool to get the physical schema of a Neo4j graph database.

    Returns:
        A dictionary containingL
        - "status": "success" or "error"
        - "schema": the schema as a JSON object if "success"
        - "error_message": the error message if "error"
    """
    driver = graphdb.get_driver()
    database_name = graphdb.database_name
    
    try:
        schema = get_structured_schema(driver, database=database_name)
        return tool_success("schema", schema)
    except Exception as e:
        return tool_error(str(e))


async def read_neo4j_cypher(
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
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

    results = graphdb.send_query(query, params)
    return results

async def write_neo4j_cypher(
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Submits a Cypher query to write to a Neo4j database.
    Make sure you have permission to write before calling this.

    Args:
        query: The Cypher query string to execute.
        params: Optional parameters to pass to the query.

    Returns:
        A list of dictionaries containing the results of the query.
        Returns an empty list "[]" if no results are found.
    """
    results = graphdb.send_query(query, params)
    return results

async def reset_neo4j_data() -> Dict[str, Any]:
    """Removes all data, indexes and constraints from the
    Neo4j database. Use with caution! Confirm with the user
    that they know this will completely reset the database.

    Returns:
        Success or an error.
    """
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


async def create_uniqueness_constraint(
    label: str,
    unique_property_key: str,
) -> Dict[str, Any]:
    """Creates a uniqueness constraint for a node label and property key.
    A uniqueness constraint ensures that no two nodes with the same label and property key have the same value.
    This improves the performance and integrity of data import and later queries.

    Args:
        label: The label of the node to create a constraint for.
        unique_property_key: The property key that should have a unique value.

    Returns:
        A dictionary with a status key ('success' or 'error').
        On error, includes an 'error_message' key.
    """    
    from agentic_kg.common.neo4j_for_adk import is_symbol
    
    # Validate input to prevent injection attacks
    if not is_symbol(label):
        return tool_error(f"Invalid label: '{label}'. Labels cannot contain spaces or be Cypher keywords.")
        
    if not is_symbol(unique_property_key):
        return tool_error(f"Invalid property key: '{unique_property_key}'. Property keys cannot contain spaces or be Cypher keywords.")
    
    # Use string formatting since Neo4j doesn't support parameterization of labels and property keys when creating a constraint
    constraint_name = f"{label}_{unique_property_key}_constraint"
    query = f"""CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
    FOR (n:{label})
    REQUIRE n.{unique_property_key} IS UNIQUE"""
    results = graphdb.send_query(query)
    return results