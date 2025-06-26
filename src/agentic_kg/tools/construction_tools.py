
from google.adk.tools import ToolContext
from typing import Dict, Any, List

from agentic_kg.common.neo4j_for_adk import (
    graphdb,
    is_write_query
)

from agentic_kg.common.util import tool_success, tool_error

APPROVED_CONSTRUCTION_PLAN = "approved_construction_plan"


def construct_node(construction_rule: dict, tool_context: ToolContext) -> Dict[str, Any]:
    """Construct a node from the construction rule."""
    batch_load_nodes_cypher = """
    LOAD CSV WITH HEADERS FROM "file:///" + $import_file AS row
    MERGE (n:$($label) {id: row[$unique_column_name]})
    SET n += row
    """
    return graphdb.send_query(batch_load_nodes_cypher, {
        "import_file": construction_rule["source_file"],
        "label": construction_rule["label"],
        "unique_column_name": construction_rule["unique_column_name"],
        "properties": construction_rule["properties"]
    })

def construct_relationship(construction_rule: dict, tool_context: ToolContext) -> Dict[str, Any]:
    """Construct a relationship from the construction rule."""
    batch_load_relationships_cypher = """
    LOAD CSV WITH HEADERS FROM "file:///" + $import_file AS row
    MATCH (from_node:$($from_node_label) {id: row[$from_node_column]})
    MATCH (to_node:$($to_node_label) {id: row[$to_node_column]})
    MERGE (from_node)-[r:$($relationship_type)]->(to_node)
    SET r += row
    """
    return graphdb.send_query(batch_load_relationships_cypher, {
        "import_file": construction_rule["source_file"],
        "from_node_label": construction_rule["from_node_label"],
        "to_node_label": construction_rule["to_node_label"],
        "from_node_column": construction_rule["from_node_column"],
        "to_node_column": construction_rule["to_node_column"],
        "relationship_type": construction_rule["relationship_type"],
        "properties": construction_rule["properties"]
    })

def build_graph_from_construction_rules(tool_context: ToolContext) -> Dict[str, Any]:
    """Build a graph from the approved construction rules."""
    if not APPROVED_CONSTRUCTION_PLAN in tool_context.state:
        return tool_error(f"{APPROVED_CONSTRUCTION_PLAN} not set.")  

    approved_construction_plan = tool_context.state[APPROVED_CONSTRUCTION_PLAN]

    print(f"Approved construction plan: {approved_construction_plan}")
    
    for construction_rule in approved_construction_plan.values():
        if construction_rule["construction_type"] == "node":
            node_results = construct_node(construction_rule, tool_context)
            if node_results["status"] == "error":
                return node_results # break out early if any node construction has an error
        elif construction_rule["construction_type"] == "relationship":
            relationship_results = construct_relationship(construction_rule, tool_context)
            if relationship_results["status"] == "error":
                return relationship_results # break out early if any relationship construction has an error
        else:
            return tool_error(f"Invalid construction type: {construction_rule['construction_type']}")
            