
from typing import Any, Dict, List, TypedDict, Union
import re

from google.adk.tools import ToolContext

from neo4j import (
    GraphDatabase,
    Transaction,
    Result,
)

from .config import load_neo4j_env
from .util import tool_success, tool_error

class Neo4jSettings(TypedDict):
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str
    neo4j_database: str

def make_driver(neo4j_settings: Neo4jSettings) -> GraphDatabase | None:
    """
    Connects to a Neo4j Graph Database according to the provided settings.
    """
    neo4j_uri = neo4j_settings["neo4j_uri"]
    neo4j_username = neo4j_settings["neo4j_username"]
    neo4j_password = neo4j_settings["neo4j_password"]

    # Initialize the driver
    driver_instance = GraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_username, neo4j_password)
    )
    return driver_instance


def is_symbol(symbol: str) -> bool:
    """Validate that a string is a valid Neo4j symbol (no spaces, not a Cypher keyword).
    
    Args:
        symbol: The string to validate
        
    Returns:
        True if the string is a valid symbol, False otherwise
    """
    # Check for spaces
    if ' ' in symbol:
        return False
        
    # Common Cypher keywords that should not be used as identifiers
    cypher_keywords = [
        'MATCH', 'RETURN', 'WHERE', 'CREATE', 'DELETE', 'REMOVE', 'SET',
        'ORDER', 'BY', 'SKIP', 'LIMIT', 'MERGE', 'ON', 'OPTIONAL', 'DETACH',
        'WITH', 'DISTINCT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AS',
        'UNION', 'ALL', 'LOAD', 'CSV', 'FROM', 'START', 'YIELD', 'CALL',
        'CONSTRAINT', 'ASSERT', 'INDEX', 'UNIQUE', 'DROP', 'EXISTS', 'USING',
        'PERIODIC', 'COMMIT', 'FOREACH', 'TRUE', 'FALSE', 'NULL', 'NOT', 'AND', 'OR', 'XOR',
        'IS', 'IN', 'STARTS', 'ENDS', 'CONTAINS'
    ]
    
    # Check if the symbol is a Cypher keyword (case-insensitive)
    if symbol.upper() in cypher_keywords:
        return False
        
    return True


def is_write_query(query: str) -> bool:
    """Check if the Cypher query performs any write operations."""
    return (
        re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE)
        is not None
    )

def result_to_adk(result: Result) -> Dict[str, Any]:
    eager_result = result.to_eager_result()
    records = [to_python(record.data()) for record in eager_result.records]
    return tool_success("query_result",records)

def to_python(value):
    from neo4j.graph import Node, Relationship, Path
    from neo4j import Record
    import neo4j.time
    if isinstance(value, Record):
        return {k: to_python(v) for k, v in value.items()}
    elif isinstance(value, dict):
        return {k: to_python(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [to_python(v) for v in value]
    elif isinstance(value, Node):
        return {
            "id": value.id,
            "labels": list(value.labels),
            "properties": to_python(dict(value))
        }
    elif isinstance(value, Relationship):
        return {
            "id": value.id,
            "type": value.type,
            "start_node": value.start_node.id,
            "end_node": value.end_node.id,
            "properties": to_python(dict(value))
        }
    elif isinstance(value, Path):
        return {
            "nodes": [to_python(node) for node in value.nodes],
            "relationships": [to_python(rel) for rel in value.relationships]
        }
    elif isinstance(value, neo4j.time.DateTime):
        return value.iso_format()
    elif isinstance(value, (neo4j.time.Date, neo4j.time.Time, neo4j.time.Duration)):
        return str(value)
    else:
        return value


class Neo4jForADK:
    """
    A wrapper for querying Neo4j which returns ADK-friendly responses.
    """
    _driver = None
    settings = None
    database_name = "neo4j"

    def __init__(self, neo4j_settings = None):
        if neo4j_settings is None:
            neo4j_settings = load_neo4j_env()
        if neo4j_settings is None:
            raise ValueError("Neo4j settings not provided and environment variables not set.")
        self.settings = neo4j_settings
        self.database_name = neo4j_settings["neo4j_database"]
        self._driver = make_driver(neo4j_settings)
    
    def get_driver(self):
        return self._driver
    
    def send_query(self, cypher_query, parameters=None) -> Dict[str, Any]:
        session = self._driver.session()
        try:
            result = session.run(
                cypher_query, 
                parameters or {},
                database_=self.database_name
            )
            return result_to_adk(result)
        except Exception as e:
            return tool_error(str(e))
        finally:
            session.close()

graphdb = Neo4jForADK()