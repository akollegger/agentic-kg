"""
Neo4j Interaction Environment

Functions for preparing an environment for consistently interacting with Neo4j.
The environment results in a single function that accepts a Cypher query string 
and returns transformed results or an error message.
"""

from typing import Optional, Dict, Any, List, Tuple, Callable, TypeVar, TypedDict
from neo4j import Driver, Result

T = TypeVar('T')

type CypherQueryParams = Dict[str, Any]

class PreparedCypherStatement(TypedDict):
    query: str
    expected_params: List[str]



"""A function that sends Cypher queries to Neo4j and returns consistently transformed result or an error message."""

def default_result_transformer(result: Result) -> List[Dict[str, Any]]:
    """
    Transforms a Neo4j Result object into a list of dictionaries, where each dictionary represents a record.

    Args:
        result (Result): The Neo4j query result object.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing the data from a record in the result.
    """
    return [record.data() for record in result]

def prepare_interaction(
    driver: Driver,
    database: str,
    result_transformer: Callable[[Result], T] = default_result_transformer
) -> Callable[[str], Callable[[Optional[Dict[str, Any]]], Tuple[T | None, str | None]]]:
    """
    Prepares a Neo4j query execution environment with a specified driver, database, and optional result transformer.
    

    Args:
        driver (Driver): The Neo4j driver instance.
        database (str): The name of the database to execute queries against.
        result_transformer (Callable[[Result], T], optional):
            A function to transform the Neo4j Result object. Defaults to default_result_transformer.

    Returns:
        CypherInteractionFunction: A function that sends Cypher queries to Neo4j and returns consistently transformed result.
    """
    def prepare(query: str) -> Callable[[Optional[Dict[str, Any]]], Tuple[T | None, str | None]]:
        """
        Prepares a Cypher query to execute against the configured Neo4j database.

        Args:
            query (str): The Cypher query string to prepare.

        Returns:
            Callable[[Optional[Dict[str, Any]]], Tuple[T | None, str | None]]: A sender function that accepts optional query parameters, returning the transformed result of the query, or an error message if execution fails.
        """
        def send(params: Optional[Dict[str, Any]] = None) -> Tuple[Optional[T], Optional[str]]:
            if params is None:
                params = {}
            try:
                result = driver.execute_query(
                    query,
                    params,
                    database_=database,
                    result_transformer_=result_transformer
                )
                return [result, None]
            except Exception as e:
                error_msg = f"Error executing query: {str(e)}"
                return [None, error_msg]
        return send
    return prepare



