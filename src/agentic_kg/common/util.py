from typing import Any, Dict

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