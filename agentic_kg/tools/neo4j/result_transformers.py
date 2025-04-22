"""
Neo4j Result Transformers

A collection of transformers for Neo4j Result objects.
"""

import json
import yaml
from neo4j import Result
from typing import List, Dict, Any

def result_to_dict(result: Result) -> List[Dict[str, Any]]:
    records = [record.data() for record in result]
    return records


def result_to_json(result: Result) -> str:
    """
    Convert a Neo4j Result object to a formatted string representation.
    
    Args:
        result: Neo4j Result object from query execution
        
    Returns:
        A formatted string representation of the results
    """
    # Convert result to list of dictionaries
    records = [record.data() for record in result]
    
    if not records:
        return "No results found."
        
    # Convert to JSON string with indentation for readability
    return json.dumps(records, indent=2, default=str)

def result_to_yaml(result: Result) -> str:
    """
    Convert a Neo4j Result object to a formatted string representation.
    
    Args:
        result: Neo4j Result object from query execution
        
    Returns:
        A formatted string representation of the results
    """
    # Convert result to list of dictionaries
    records = [record.data() for record in result]
    
    if not records:
        return "No results found."
        
    # Convert to YAML string with indentation for readability
    return yaml.dump(records)


