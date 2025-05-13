from google.adk.agents import Agent

from google.adk.models.lite_llm import LiteLlm


from agentic_kg.common.config import model_roles
from agentic_kg.sub_agents import cypher_agent

from .prompts import instructions

just_cypher_agent = Agent(
        name="kg_agent_v1",
        model=LiteLlm(model=model_roles["chat"]),
        description="Knowledge graph construction using Neo4j and cypher.", # Crucial for delegation later
        
        instruction=instructions["just_cypher_v1"],
        tools=[], # Make the tool available to this agent
        sub_agents=[cypher_agent]
    )

root_agent = just_cypher_agent