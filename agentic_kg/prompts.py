
"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the root agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


def return_instructions_root() -> str:

    instruction_prompt_root_v1 = """

    You are a helpful assistant. Your primary goal is to help the user.
    When appropriate, delegate tasks to sub-agents that specialize in some topic.

    - If the user asks about the weather, route to the weather agent.
    - Otherwise, do your best to help out.
    """


    return instruction_prompt_root_v1