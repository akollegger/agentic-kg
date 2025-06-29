from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import agent_tool

from typing import AsyncGenerator
from google.adk.events import Event, EventActions

from agentic_kg.common.config import llm
from agentic_kg.tools import get_proposed_schema, approve_proposed_schema, finished

from .variants import variants

AGENT_NAME = "schema_extension_agent_v3"
schema_extension_agent = LlmAgent(
    name=AGENT_NAME,
    description="Proposes a knowledge graph schema based on the user goal and approved file list, taking into consideration feedback if available.",
    model=llm,
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

# CRITIC_NAME = "schema_critic_agent_v2"
# schema_critic_agent = LlmAgent(
#     name=CRITIC_NAME,
#     description="Criticizes the proposed schema for relevance to the user goal and approved files.",
#     model=llm,
#     instruction=variants[CRITIC_NAME]["instruction"],
#     tools=variants[CRITIC_NAME]["tools"], 
#     output_key="feedback"
# )

# class CheckStatusAndEscalate(BaseAgent):
#     async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
#         feedback = ctx.session.state.get("feedback", "valid")
#         should_stop = (feedback == "valid")
#         yield Event(author=self.name, actions=EventActions(escalate=should_stop))

# refinement_loop = LoopAgent(
#     name="schema_refinement_loop",
#     max_iterations=2,
#     sub_agents=[schema_extension_agent, schema_critic_agent, CheckStatusAndEscalate(name="StopChecker")]
# )

# multi_agent_coordinator = LlmAgent(
#     name="schema_extension_agent_coordinator",
#     model=llm,
#     instruction="""
#     You are a coordinator for the schema proposal process. Use tools to propose a schema to the user.
#     If the user disapproves, use the tools to refine the schema and ask the user to approve again.
#     If the user approves, use the 'approve_proposed_schema' tool to record the approval.
#     When the schema approval has been recorded, use the 'finished' tool.

#     1. Use the 'refinement_loop' tool to determine a schema with construction rules
#     2. Use the 'get_proposed_schema' tool to get the proposed schema
#     3. Present the proposed schema and state['construction_rules'] to the user for approval
#     4. If they disapprove, consider their feedback and go back to step 1
#     5. If the user approves, use the 'approve_proposed_schema' tool to record the approval
#     6. When the schema approval has been recorded, use the 'finished' tool
#     """,
#     tools=[agent_tool.AgentTool(refinement_loop), get_proposed_schema, get_proposed_schema, approve_proposed_schema, finished]
# )

root_agent = schema_extension_agent