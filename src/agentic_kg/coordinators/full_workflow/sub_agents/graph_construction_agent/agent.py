from google.adk.agents import Agent

from agentic_kg.common.config import llm

# variants are pairs of instructions with tools
from .variants import variants

AGENT_NAME = "graph_construction_agent_v3"
graph_construction_agent = Agent(
        name=AGENT_NAME,
        model=llm,
        description="Knowledge graph construction based on approved construction rules.", 
        instruction=variants[AGENT_NAME]["instruction"],
        tools=variants[AGENT_NAME]["tools"]
    )

root_agent = graph_construction_agent