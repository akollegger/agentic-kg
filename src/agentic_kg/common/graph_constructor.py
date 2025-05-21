"""
A graph constructor takes a graph plan and constructs a knowledge graph 
by applying the construction rules in the plan.
"""

from typing import Dict, Callable

from agentic_kg.common.graph_plan import GraphPlan
from agentic_kg.common.neo4j_for_adk import graphdb
from agentic_kg.common.util import tool_success, tool_error

def load_csv_nodes(file_name: str, node_label: str, node_id_field: str) -> Dict[str, str]:
    """Load nodes from a CSV file."""
    print(f"Loading nodes from CSV file: {file_name}")
    
    import_dir_result = graphdb.get_import_directory()
    if import_dir_result["status"] == "error": return import_dir_result
    import_dir = import_dir_result["neo4j_import_dir"]
    
    from pathlib import Path
    file_path = Path(import_dir) / Path(file_name)
    if not file_path.exists():
        return tool_error(f"File does not exist in import directory: {file_name}")
    
    return graphdb.send_query(
        """
        LOAD CSV WITH HEADERS FROM "file:///" + $import_file AS row
        MERGE (n:$($node_label) {id: row[$node_id_field]})
        SET n += row
        """,
        {
            "import_file": file_name,
            "node_label": node_label,
            "node_id_field": node_id_field
        }
    )

def load_csv_relationships(file_name: str, from_label:str, from_id_field: str, to_label:str, to_id_field: str, relationship_type: str) -> Dict[str, str]:
    """Load relationships from a CSV file."""
    print(f"Loading relationships from CSV file: {file_name}")
    
    import_dir_result = graphdb.get_import_directory()
    if import_dir_result["status"] == "error": return import_dir_result
    import_dir = import_dir_result["neo4j_import_dir"]
    
    from pathlib import Path
    import_path = Path(import_dir) / Path(file_name)
    if not import_path.exists():
        return tool_error(f"File does not exist in import directory: {file_name}")
        
    return graphdb.send_query(
        """
        LOAD CSV WITH HEADERS FROM "file:///" + $import_file AS row
        MATCH (from_node:$($from_label) {id: row[$from_id_field]}), (to_node:$($to_label) {id: row[$to_id_field]})
        MERGE (from_node)-[r:$($relationship_type)]->(to_node)
        SET r += row
        """,
        {
            "import_file": file_name,
            "from_label": from_label,
            "from_id_field": from_id_field,
            "to_label": to_label,
            "to_id_field": to_id_field,
            "relationship_type": relationship_type
        }
    )
    
    return tool_success("load_csv_relationships", f"Loaded relationships from {file_name}")

# Dictionary mapping tool names to their implementation functions
TOOL_MAP: Dict[str, Callable] = {
    "load_csv_nodes": load_csv_nodes,
    "load_csv_relationships": load_csv_relationships
}

def construct_graph(graph_plan: GraphPlan):
    """Construct a graph on Neo4j according to a GraphPlan. 
    Uses the graphdb singleton from neo4j_for_adk.
    
    This function processes all construction rules in the graph plan in the following order:
    1. Process entity construction rules to create nodes
    2. Process relation construction rules to create relationships
    
    Args:
        graph_plan: The graph plan to construct
        
    Returns:
        A dictionary with status information about the construction process
    """
    results = []
    
        # 1. Process entity construction rules to create nodes
    for entity in graph_plan.entities.values():
        for rule in entity.rules:
            if rule.is_construction():
                print(f"Executing construction rule '{rule.tool}' for entity {entity.name}")
                if rule.tool in TOOL_MAP:
                    result = TOOL_MAP[rule.tool](**rule.args)
                    if result["status"] == "error":
                        return result
                    results.append({
                        "entity": entity.name,
                        "rule": rule.tool,
                        "result": result
                    })
                else:
                    print(f"Unknown tool: {rule.tool}")
    
    # 2. Process relation construction rules to create relationships
    for relation in graph_plan.relations.values():
        for rule in relation.rules:
            if rule.is_construction():
                print(f"Executing construction rule '{rule.tool}' for relation {relation.name}")
                if rule.tool in TOOL_MAP:
                    result = TOOL_MAP[rule.tool](**rule.args)
                    if result["status"] == "error":
                        return result
                    results.append({
                        "relation": relation.name,
                        "rule": rule.tool,
                        "result": result
                    })
                else:
                    print(f"Unknown tool: {rule.tool}")
                
    return {"status": "success", "results": results}