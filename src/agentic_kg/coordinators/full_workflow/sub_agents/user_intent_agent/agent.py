from google.adk.agents import Agent

from agentic_kg.common.config import llm
from .sub_agents import cypher_agent

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "user_intent_agent_v1"
user_intent_agent = Agent(
        name=AGENT_NAME,
        model=llm,
        description="Knowledge graph ideation with a user.", 
        instruction=variants[AGENT_NAME]["instruction"],
        tools=variants[AGENT_NAME]["tools"]
    )

root_agent = user_intent_agent