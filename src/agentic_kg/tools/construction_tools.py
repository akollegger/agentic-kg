
from google.adk.tools import ToolContext
from typing import Dict, Any, List

from agentic_kg.common.util import tool_success, tool_error

CONSTRUCTION_RULES = "construction_rules"
def add_construction_rule(rule_name:str, file_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    f"""Adds a construction rule to the {CONSTRUCTION_RULES}

    Args:
        rule_name: The name of the rule to add
        file_name: The name of the file to which the rule applies

    Returns:
        dict: A dictionary containing success or failure information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a {CONSTRUCTION_RULES} key with list of rules.
              If 'error', includes an 'error_message' key.
    """
    if not CONSTRUCTION_RULES in tool_context.state:
        construction_rules = []
    else: 
        construction_rules = tool_context.state[CONSTRUCTION_RULES]

    construction_rules.append({"rule_name": rule_name, "file_name": file_name})

    tool_context.state[CONSTRUCTION_RULES] = construction_rules

    return tool_success(CONSTRUCTION_RULES, tool_context.state[CONSTRUCTION_RULES])
