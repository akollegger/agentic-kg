import os
from typing import Any, Dict, List, TypedDict, Union
import re
import atexit

from neo4j import (
    GraphDatabase,
    Result,
)

def tool_success(key:str,result: Any) -> Dict[str, Any]:
    """Convenience function to return a success result."""
    return {
        'status': 'success',
        key: result
    }

def tool_error(message: str) -> Dict[str, Any]:
    """Convenience function to return an error result."""
    return {
        'status': 'error',
        'error_message': message
    }


class Neo4jSettings(TypedDict):
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str
    neo4j_database: str


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
    database_name = "neo4j"

    def __init__(self):
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME") or "neo4j"
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        neo4j_database = os.getenv("NEO4J_DATABASE") or os.getenv("NEO4J_USERNAME") or "neo4j"
        self.database_name = neo4j_database
        self._driver =  GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_username, neo4j_password)
        )
    
    def get_driver(self):
        return self._driver
    
    def close(self):
        return self._driver.close()
    
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

    def get_import_directory(self):
        results = self.send_query("""
            Call dbms.listConfig() YIELD name, value
            WHERE name CONTAINS 'server.directories.import'
            RETURN value as import_dir
            """)
        if results["status"] == "success":
            return tool_success("neo4j_import_dir",results["query_result"][0]["import_dir"])
        else:
            return tool_error(results["error_message"])


graphdb = Neo4jForADK()

# Register cleanup function to close database connection on exit
atexit.register(graphdb.close)