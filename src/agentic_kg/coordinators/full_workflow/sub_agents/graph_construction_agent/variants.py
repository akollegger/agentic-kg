
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the root agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""

from agentic_kg.tools import (
    get_user_goal, read_neo4j_cypher, write_neo4j_cypher, create_uniqueness_constraint, 
    get_approved_schema, get_approved_files,
    finished
)

variants = {
    # graph_construction_agent_v1
    # Benefits:
    # - simple workflow
    "graph_construction_agent_v1": {
        "instruction": """
        You are an expert at knowledge graph construction. Construct a graph using
        the available tools, according to the approved schema and files.

        Before beginning construction, make sure you know the user goal and available
        files. Use the get_user_goal and get_approved_files tools.

        When constructing a graph from files always follow the graph schema. Follow these steps:
        1. create appropriate constraints for nodes with unique IDs
        2. load all node files first
        3. finally load all relationship files

        """,
        "tools": [get_user_goal, get_approved_schema, get_approved_files, read_neo4j_cypher, write_neo4j_cypher, create_uniqueness_constraint, finished]
    },
}
