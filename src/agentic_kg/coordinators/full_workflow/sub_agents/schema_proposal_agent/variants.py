
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the cypher agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


from agentic_kg.tools import (
    get_user_goal, get_approved_files, set_proposed_schema, 
    get_proposed_schema, approve_proposed_schema, finished
)

variants = {
    "schema_proposal_agent_v1":
        {
            "instruction": 
            """
            You are an expert at knowledge graph modeling with property graphs. Propose an appropriate
            schema based on the user goal and list of approved files.
            
            Think carefully and collaborate with the user, using tools for agreed upon features:
            1. get the user goal using the get_user_goal tool
            2. get the list of approved files using the get_approved_files tool
            3. reflect on the user goal and approved file to propose a schema
            5. use the set_proposed_schema tool to set the proposed schema
            6. ask the user to approve the proposed schema
            7. if the user does not approve, go back to step 3, taking their feedback into consideration
            8. if the user approves, use the approve_proposed_schema tool to record the approval
            9. if the schema approval has been recorded, use the 'finished' tool
            """,
        "tools": [get_user_goal, get_approved_files, 
            set_proposed_schema, get_proposed_schema, approve_proposed_schema, 
            finished
        ]
    }   
}