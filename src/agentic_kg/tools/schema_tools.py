from google.adk.tools import ToolContext
from typing import Dict, Any
from agentic_kg.common.util import tool_success, tool_error

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