
from typing import Any, Optional, Dict, List

from google.adk.tools import ToolContext

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

from neo4j import GraphDatabase


from neo4j_graphrag.schema import get_structured_schema

from .neo4j_utils import (
    acquire_driver, 
    transactional_read, 
    is_write_query, 
    to_python, 
    tool_success, tool_error
)

def ensure_neo4j_settings(tool_context: ToolContext) -> bool:
    if "neo4j_settings" not in tool_context.state:
        return False
    return True


async def neo4j_is_ready(
    tool_context: ToolContext,
):
    """Tool to check that the Neo4j database is ready.
    Replies with either a positive message about the database being ready or an error message.
    """
    if not ensure_neo4j_settings(tool_context):
        return tool_error("Neo4j has not been configured.")

    neo4j_database = tool_context.state["neo4j_settings"]["neo4j_database"]

    driver = acquire_driver(tool_context.state["neo4j_settings"])

    if driver is None:
        return tool_error("Could not connect to Neo4j.")

    try:
        driver.verify_connectivity()
        with driver.session(database=neo4j_database) as session:
            result = session.run("RETURN 'Neo4j is ready!' as message")
            record = result.single()
            return tool_success(record["message"])
    except Exception as e:
        return tool_error(str(e))
    
async def get_physical_schema(
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Tool to get the physical schema of a Neo4j graph database.

    The schema is returned as a JSON object containing a description
    of the node labels and relationship types.
    """
    if not ensure_neo4j_settings(tool_context):
        return tool_error("Neo4j has not been configured.")
    
    neo4j_database = tool_context.state["neo4j_settings"]["neo4j_database"]
    
    driver = acquire_driver(tool_context.state["neo4j_settings"])
    
    if driver is None:
        return tool_error("Could not connect to Neo4j.")
    
    try:
        schema = get_structured_schema(driver, database=neo4j_database)
        return tool_success(schema)
    except Exception as e:
        return tool_error(str(e))


async def read_neo4j_cypher(
    query: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    tool_context: ToolContext,
) -> List[Dict[str, Any]]:
    """Submits a Cypher query to read from Neo4j database.

    Args:
        query: The Cypher query string to execute.
        params: Optional parameters to pass to the query.

    Returns:
        A list of dictionaries containing the results of the query.
        Returns an empty list "[]" if no results are found.

    """

    if not ensure_neo4j_settings(tool_context):
        return tool_error("Neo4j has not been configured.")
    
    if is_write_query(query):
        return tool_error("Only MATCH queries are allowed for read-query")

    neo4j_database = tool_context.state["neo4j_settings"]["neo4j_database"]

    driver = acquire_driver(tool_context.state["neo4j_settings"])

    if driver is None:
        return tool_error("Could not connect to Neo4j.")

    print("Driver acquired, attempting to execute query:" + query)
    try:
        with driver.session(database=neo4j_database) as session:
            results = session.execute_read(transactional_read, query, params)
            print("Results: " + str(results))
            return tool_success(results)
    except Exception as e:
        return tool_error(str(e))
