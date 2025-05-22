from google.adk.tools import ToolContext
from agentic_kg.common.util import tool_success

def set_kind_of_graph(kind_of_graph: str, graph_description:str, tool_context: ToolContext):
    """Sets the kind of graph and its description based on approval from the user.
    
    Args:
        kind_of_graph: 2-3 word definition of the kind of graph, for example "recent US patents"
        graph_description: a single paragraph description of the graph, summarizing the user's intent
    """
    tool_context.state["kind_of_graph"] = kind_of_graph
    tool_context.state["graph_description"] = graph_description

    return tool_success("kind_of_graph", kind_of_graph)