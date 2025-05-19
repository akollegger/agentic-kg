from google.adk.tools import ToolContext

from agentic_kg.common.util import tool_success

def set_kind_of_graph(kind_of_graph: str, tool_context: ToolContext):
    tool_context.state["kind_of_graph"] = kind_of_graph
    return tool_success("kind_of_graph", "Kind of graph set to: " + kind_of_graph)

