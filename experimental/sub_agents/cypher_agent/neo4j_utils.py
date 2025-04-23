
from typing import Any, Dict, List, TypedDict
import re

from google.adk.tools import ToolContext

from neo4j import (
    GraphDatabase,
    Transaction,
    Result,
)


from neo4j.exceptions import DatabaseError


def tool_success(result: Any):
    return {
        'status': 'success',
        'query_result': result
    }

def tool_error(message: str):
    return {
        'status': 'error',
        'error_message': message
    }

class Neo4jSettings(TypedDict):
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str
    neo4j_database: str

def acquire_driver(neo4j_settings: Neo4jSettings) -> GraphDatabase | None:
    neo4j_uri = neo4j_settings["neo4j_uri"]
    neo4j_username = neo4j_settings["neo4j_username"]
    neo4j_password = neo4j_settings["neo4j_password"]
    # Initialize the driver
    driver = GraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_username, neo4j_password)
    )

    return driver



def is_write_query(query: str) -> bool:
    """Check if the Cypher query performs any write operations."""
    return (
        re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE)
        is not None
    )

def transactional_read(tx: Transaction, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_results = tx.run(query, params)
    eager_results = raw_results.to_eager_result()
    return result_to_dict(eager_results)


def result_to_dict(result: Result) -> List[Dict[str, Any]]:
    records = [to_python(record.data()) for record in result.records]
    return records

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
