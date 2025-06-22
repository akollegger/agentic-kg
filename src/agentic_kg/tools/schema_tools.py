from google.adk.tools import ToolContext
from typing import Dict, Any
from agentic_kg.common.util import tool_success, tool_error
from .file_tools import search_file

PROPOSED_SCHEMA = "proposed_schema"
APPROVED_SCHEMA = "approved_schema"

def set_proposed_schema(graph_schema: str, tool_context: ToolContext) -> Dict[str, Any]:
    f"""Saves a proposed graph schema into state using key {PROPOSED_SCHEMA}

    Args:
        graph_schema: 
    """
    tool_context.state[PROPOSED_SCHEMA] = graph_schema
    return tool_success(PROPOSED_SCHEMA, graph_schema)

def get_proposed_schema(tool_context: ToolContext) -> Dict[str, Any]:
    """Returns the current graph schema proposal."""
    if PROPOSED_SCHEMA not in tool_context.state:
        return tool_error(f"{PROPOSED_SCHEMA} not set.")  

    return tool_success(PROPOSED_SCHEMA, tool_context.state[PROPOSED_SCHEMA])


def approve_proposed_schema(tool_context:ToolContext) -> Dict[str, Any]:
    f"""Approves the {PROPOSED_SCHEMA} in state for further processing as {APPROVED_SCHEMA}."""
    
    if PROPOSED_SCHEMA not in tool_context.state:
        return tool_error(f"{PROPOSED_SCHEMA} not set")

    tool_context.state[APPROVED_SCHEMA] = tool_context.state[PROPOSED_SCHEMA]


def get_approved_schema(tool_context: ToolContext) -> Dict[str, Any]:
    """Returns the approved graph schema, if it there is one."""
    if APPROVED_SCHEMA not in tool_context.state:
        return tool_error(f"{APPROVED_SCHEMA} not set.")  

    return tool_success(APPROVED_SCHEMA, tool_context.state[APPROVED_SCHEMA])

#  Tool: Propose Node Construction

PROPOSED_CONSTRUCTION_PLAN = "proposed_construction_plan"
NODE_CONSTRUCTION = "node_construction"

def propose_node_construction(approved_file: str, proposed_label: str, unique_column_name: str, proposed_properties: list[str], tool_context:ToolContext) -> dict:
    f"""Propose a node construction for an approved file that supports the user goal.

    The construction plan will be saved to {PROPOSED_CONSTRUCTION_PLAN} list of dictionaries.
    Each dictionary will have the following keys:
    - construction_type: "node"
    - source_file: The approved file to propose a node construction for
    - label: The label of the node
    - unique_column_name: The name of the column that will be used to uniquely identify constructed nodes
    - properties: A list of properties for the node

    Args:
        approved_file: The approved file to propose a node construction for
        proposed_label: The proposed label for constructed nodes
        unique_column_name: The name of the column that will be used to uniquely identify constructed nodes
        tool_context: The tool context

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a {NODE_CONSTRUCTION} key with the construction plan for the node
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    # quick sanity check -- does the approved file have the unique column?
    search_results = search_file(approved_file, unique_column_name, tool_context)
    if search_results["status"] == "error":
        return search_results
    if search_results["search_results"]["metadata"]["lines_found"] == 0:
        return tool_error(f"{approved_file} does not have the column {unique_column_name}. Check the file content and try again.")

    construction_plan = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, [])
    node_construction_rule = {
        "construction_type": "node",
        "source_file": approved_file,
        "label": proposed_label,
        "unique_column_name": unique_column_name,
        "properties": proposed_properties
    }   
    construction_plan.append(node_construction_rule)
    tool_context.state[PROPOSED_CONSTRUCTION_PLAN] = construction_plan
    return tool_success(NODE_CONSTRUCTION, node_construction_rule)

#  Tool: Propose Relationship Construction

RELATIONSHIP_CONSTRUCTION = "relationship_construction"

def propose_relationship_construction(approved_file: str, proposed_relationship_type: str, 
    from_node_label: str,from_node_column: str, to_node_label:str, to_node_column: str, 
    proposed_properties: list[str], 
    tool_context:ToolContext) -> dict:
    f"""Propose a relationship construction for an approved file that supports the user goal.

    The construction plan will be saved to {PROPOSED_CONSTRUCTION_PLAN} list of dictionaries.

    Args:
        approved_file: The approved file to propose a node construction for
        proposed_relationship_type: The proposed label for constructed relationships
        from_node_label: The label of the source node
        from_node_column: The name of the column within the approved file that will be used to uniquely identify source nodes
        to_node_label: The label of the target node
        to_node_column: The name of the column within the approved file that will be used to uniquely identify target nodes
        unique_column_name: The name of the column that will be used to uniquely identify target nodes

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a {RELATIONSHIP_CONSTRUCTION} key with the construction plan for the node
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    # quick sanity check -- does the approved file have the from_node_column?
    search_results = search_file(approved_file, from_node_column, tool_context)
    if search_results["status"] == "error":
      return search_results  
    if search_results["search_results"]["metadata"]["lines_found"] == 0:
        return tool_error(f"{approved_file} does not have the from node column {from_node_column}. Check the content of the file and reconsider the relationship.")

    # quick sanity check -- does the approved file have the to_node_column?
    search_results = search_file(approved_file, to_node_column, tool_context)
    if search_results["status"] == "error" or search_results["search_results"]["metadata"]["lines_found"] == 0:
        return tool_error(f"{approved_file} does not have the to node column {to_node_column}. Check the content of the file and reconsider the relationship.")

    construction_plan = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, [])
    relationship_construction_rule = {
        "construction_type": "relationship",
        "source_file": approved_file,
        "relationship_type": proposed_relationship_type,
        "from_node_label": from_node_label,
        "from_node_column": from_node_column,
        "to_node_label": to_node_label,
        "to_node_column": to_node_column,
        "properties": proposed_properties
    }   
    construction_plan.append(relationship_construction_rule)
    tool_context.state[PROPOSED_CONSTRUCTION_PLAN] = construction_plan
    return tool_success(RELATIONSHIP_CONSTRUCTION, relationship_construction_rule)

APPROVED_CONSTRUCTION_PLAN = "approved_construction_plan"

# Tool: Approve the proposed construction plan
def approve_proposed_construction_plan(tool_context:ToolContext) -> dict:
    """Approve the proposed construction plan."""
    tool_context.state[APPROVED_CONSTRUCTION_PLAN] = tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN)
    return tool_success(APPROVED_CONSTRUCTION_PLAN, tool_context.state[APPROVED_CONSTRUCTION_PLAN])

# Tool: Get Proposed construction Plan

def get_proposed_construction_plan(tool_context:ToolContext) -> dict:
    """Get the proposed construction plan."""
    return tool_context.state.get(PROPOSED_CONSTRUCTION_PLAN, [])


def get_approved_construction_plan(tool_context:ToolContext) -> dict:
    """Get the approved construction plan."""
    return tool_context.state.get(APPROVED_CONSTRUCTION_PLAN, [])