
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the cypher agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


from agentic_kg.tools import get_user_goal, sample_csv_file, sample_markdown_file

variants = {
    "schema_suggestion_agent_v1":
        {
            "instruction": 
            """
            You are an expert at knowledge graph modeling for property graphs. Propose an appropriate
            schema for the kind of graph '{{user_goal}}' based on the list of files '{{current_file_list}}'.
            """,
        "tools": [get_user_goal, sample_csv_file, sample_markdown_file]
    }   
}