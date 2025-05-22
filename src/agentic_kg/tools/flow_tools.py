from google.adk.tools import ToolContext

def finished(tool_context: ToolContext):
    """Approves the current workflow step, deferring back to a parent.
    """
    tool_context.actions.escalate = True
    tool_context.actions.transfer_to_agent = tool_context._invocation_context.agent.parent_agent.name
    return {}
