from google.adk.tools import ToolContext
from agentic_kg.common.util import tool_success, tool_error
from agentic_kg.tools.cypher_tools import merge_singleton_node_into_graph, read_neo4j_cypher

def set_user_goal(kind_of_graph: str, graph_description:str, tool_context: ToolContext):
    """Sets the user's goal, including the kind of graph and its description.
    
    Args:
        kind_of_graph: 2-3 word definition of the kind of graph, for example "recent US patents"
        graph_description: a single paragraph description of the graph, summarizing the user's intent
    """
    user_goal_data = {"kind_of_graph": kind_of_graph, "graph_description": graph_description}
    tool_context.state["user_goal"] = user_goal_data
    tool_context.state["user_goal_approved"] = True
    return tool_success("user_goal", user_goal_data)

def get_user_goal(tool_context: ToolContext):
    """Returns the user's goal, which is a dictionary containing the kind of graph and its description."""
    if "user_goal" not in tool_context.state:
        return tool_error("user_goal not set. Ask the user to clarify their goal (kind of graph and description).")  
    
    user_goal_data = tool_context.state["user_goal"]

    return tool_success("user_goal", user_goal_data)

#  Define the tools for the User Intent Agent

def set_perceived_user_goal(kind_of_graph: str, graph_description:str, tool_context: ToolContext):
    """Sets the user's goal, including the kind of graph and its description.
    
    Args:
        kind_of_graph: 2-3 word definition of the kind of graph, for example "recent US patents"
        graph_description: a single paragraph description of the graph, summarizing the user's intent
    """
    user_goal_data = {"kind_of_graph": kind_of_graph, "graph_description": graph_description}
    tool_context.state["perceived_user_goal"] = user_goal_data
    print("User's goal set:", user_goal_data)
    return tool_success("perceived_user_goal", user_goal_data)

def approve_perceived_user_goal(tool_context: ToolContext):
    """Approves the user's goal, including the kind of graph and its description."""
    if "perceived_user_goal" not in tool_context.state:
        return tool_error("perceived_user_goal not set. Ask the user to clarify their goal (kind of graph and description).")
    
    tool_context.state["approved_user_goal"] = tool_context.state["perceived_user_goal"]

    return tool_success("approved_user_goal", tool_context.state["approved_user_goal"])

def get_approved_user_goal(tool_context: ToolContext):
    """Returns the user's goal, which is a dictionary containing the kind of graph and its description."""
    if "approved_user_goal" not in tool_context.state:
        return tool_error("approved_user_goal not set. Ask the user to clarify their goal (kind of graph and description).")  
    
    user_goal_data = tool_context.state["approved_user_goal"]

    return tool_success("approved_user_goal", user_goal_data)
