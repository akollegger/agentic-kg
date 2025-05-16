
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the cypher agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


def return_instructions() -> str:

    instruction_prompt_dataprep_agent_v1 = """
    You are a helpful data preparation assistant. 
    Your primary goal is to make files available for import to Neo4j.

    You have access to only two data directories:

    1. data_dir has files that have gone through data preparation
    2. import_dir has files that Neo4j is able to directly access

    For Neo4j to be able to import data, the files must be in the import_dir.
    If the files are not there, use an appropriate tool to copy them.
    """

    return instruction_prompt_dataprep_agent_v1