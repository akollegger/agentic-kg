
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the root agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""

from agentic_kg.tools import get_user_goal, read_neo4j_cypher, write_neo4j_cypher, create_uniqueness_constraint, finished

variants = {
    # graph_construction_agent_v1
    # Benefits:
    # - simple workflow
    "graph_construction_agent_v1": {
        "instruction": """
        You are an expert at knowledge graph construction.

        """,
        "tools": [get_user_goal, read_neo4j_cypher, write_neo4j_cypher, create_uniqueness_constraint, finished]
    },
}
