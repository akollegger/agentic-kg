from google.adk.tools import ToolContext

from neo4j_for_adk import tool_success, tool_error

def get_approved_user_goal(tool_context: ToolContext):
    """Returns the user's goal, which is a dictionary containing the kind of graph and its description."""
    if "approved_user_goal" not in tool_context.state:
        return tool_error("approved_user_goal not set. Ask the user to clarify their goal (kind of graph and description).")  
    
    user_goal_data = tool_context.state["approved_user_goal"]

    return tool_success("approved_user_goal", user_goal_data)
