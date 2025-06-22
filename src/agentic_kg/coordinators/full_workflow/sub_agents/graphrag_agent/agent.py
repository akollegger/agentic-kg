from google.adk.agents import Agent

from agentic_kg.common.config import llm
from agentic_kg.tools import finished

from .variants import variants

AGENT_NAME = "graphrag_agent_v1"
graphrag_agent = Agent(
    name=AGENT_NAME,
    model=llm,
    description="Information retrieval from a knowledge graph using a range of query tools.", # Crucial for delegation later
    instruction=variants[AGENT_NAME]["instruction"],
    tools=variants[AGENT_NAME]["tools"], 
)

root_agent = graphrag_agent