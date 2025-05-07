
from typing import Any, Dict, List, TypedDict, Union
import re

from google.adk.tools import ToolContext

from neo4j import (
    GraphDatabase,
    Transaction,
    Result,
)

class ToolSuccessResult(TypedDict):
    status: str  # 'success'
    query_result: List[Dict[str, any]]

class ToolErrorResult(TypedDict):
    status: str  # 'error'
    error_message: str

ToolResult = Union[ToolSuccessResult, ToolErrorResult]

def tool_success(result: List[Dict[str, Any]]) -> ToolSuccessResult:
    return {
        'status': 'success',
        'query_result': result
    }

def tool_error(message: str) -> ToolErrorResult:
    return {
        'status': 'error',
        'error_message': message
    }

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


def is_write_query(query: str) -> bool:
    """Check if the Cypher query performs any write operations."""
    return (
        re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE)
        is not None
    )

def result_to_adk(result: Result) -> Dict[str, Any]:
    eager_result = result.to_eager_result()
    records = [to_python(record.data()) for record in eager_result.records]
    return tool_success(records)

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
    A singleton interface for sending queries to Neo4j and getting
    ADK-friendly responses.
    Usage:
        ADKfriendlyNeo4j.initialize(settings)
        db = ADKfriendlyNeo4j.get_driver()
        result = db.send_query("MATCH (n) RETURN n LIMIT 1")
    """
    _instance = None
    _settings = None

    def __init__(self, neo4j_settings):
        if Neo4jForADK._settings:
            return
        self.driver = make_driver(neo4j_settings)
        Neo4jForADK._settings = neo4j_settings

    @classmethod
    def initialize(cls, neo4j_settings):
        if cls._instance is None:
            cls._instance = cls(neo4j_settings)
        return cls._instance

    @classmethod
    def get_graphdb(cls):
        if cls._instance is None:
            raise Exception("ADKfriendlyNeo4j must be initialized with settings before use.")
        return cls._instance

    def get_driver(self):
        return self.driver
    
    def send_query(self, cypher_query, parameters=None) -> ToolResult:
        neo4j_database = self._settings["neo4j_database"]
        session = self.driver.session()
        try:
            result = session.run(
                cypher_query, 
                parameters or {},
                database_=neo4j_database
            )
            return result_to_adk(result)
        except Exception as e:
            return tool_error(str(e))
        finally:
            session.close()