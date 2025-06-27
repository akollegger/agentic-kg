from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

from agentic_kg.common.config import llm

from agentic_kg.tools import get_approved_user_goal, get_physical_schema, get_approved_files, get_approved_schema, extend_approved_user_goal
from .sub_agents import unstructured_files_agent, schema_extension_agent, graph_extension_agent

def preset_context_state(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    # Only preset if the user goal does not already exist. This ensures initialization happens only once
    if "approved_user_goal" not in callback_context.state:
        callback_context.state["approved_user_goal"] = {
                "kind_of_graph": "bill of materials",
                "graph_description": "A multi-level bill of materials for manufactured products, useful for root cause analysis."
            }
    return None # Allow the model call to proceed


unstructured_extension_agent = LlmAgent(
    name="unstructured_extension_agent_v1",
    description="""Extends a knowledge graph with data from unstructured source files.""",
    model=llm,
    instruction="""You are helpful guide that is an expert in knowledge graph construction using Neo4j.
        Your primary goal is to guide the user through the process of adding
        unstructured data to an existing knowledge graph.

        Requirements:
        - use the 'get_physical_schema' tool to get the physical schema of the existing knowledge graph
        - use the 'get_approved_user_goal' tool to understand the motivation of the graph that has been constructed

        Follow this sequence, delegating to sub-agents as appropriate:
        1. Extend the user's goal to include the purpose of adding unstructured data using the 'extend_approved_user_goal' tool
        2. Check that the requirements are met, and share your findings with the user
        3. If the requirements are met, delegate to the unstructured_files_agent to suggest files to use for import
        4. Once you have approved files, delegate to the schema_extension_agent to design an extended graph schema that incorporates the unstructured data
        5. Once you have approved the schema, delegate to the graph_extension_agent to construct the graph
        """,
    sub_agents=[unstructured_files_agent, schema_extension_agent, graph_extension_agent],
    tools=[get_approved_user_goal, extend_approved_user_goal, get_physical_schema, get_approved_files, get_approved_schema],
    before_model_callback=preset_context_state
)

root_agent = unstructured_extension_agent