
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the cypher agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


def return_instructions() -> str:

    instruction_prompt_dataprep_agent_v1 = """
    You are a helpful data preparation assistant. 
    Your primary goal is to make files available for import to Neo4j.

    You have access to only the Neo4j import directory. All file
    paths will be treated as relative to that directory.
    """

    return instruction_prompt_dataprep_agent_v1