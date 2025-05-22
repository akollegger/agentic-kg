from typing import Any, Dict
from google.adk.tools import ToolContext

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


def get_state_value_or_else(key:str, error_message:str, tool_context:ToolContext) -> dict:
    """Gets a state value or else returns an error.
    Both the success and error values are returned as an ADK-friendly dict.
    """
    if key in tool_context.state:
        return tool_success(key,tool_context.state[key])
    else:
        return tool_error(error_message)