from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import ToolContext

from agentic_kg.common.config import llm
from agentic_kg.common.util import tool_success

from agentic_kg.sub_agents.dataprep_agent.tools import list_import_files, sample_file

from pydantic import BaseModel, Field

STATE_CURRENT_FILES = "current_file_list"

class FileSuggestionsInput(BaseModel):
    kind_of_graph: str = Field(description="The kind of graph to construct.")
    current_file_list: list[str] = Field(description="The current list of files to suggest.")

initial_file_listing = Agent(
    name="initial_file_listing_agent",
    description="List all available import files.",
    instruction="""Use tools to list all available import files. Output a bullet list of the files. Do not add any extra text.""",
    model=llm,
    tools=[list_import_files],
    output_key=STATE_CURRENT_FILES,
)

file_critic = Agent(
    name="file_critic",
    description="Criticize the file list for relevance to the kind of graph indicated by the 'kind_of_graph' key in session state.",
    model=llm,
    instruction=f"""You are a Constructive Critic AI reviewing a list of files. Your goal is to filter relevant files.

    **File List to Critique:**
    ```
    {{current_file_list}}
    ```

    **Task:**
    Review each file in the list for relevance to the kind of graph '{{kind_of_graph}}'. When evaluating relevance,
    take into account the explicit strictness of the kind, e.g. "just this" implies narrow strictness, while "this and related" implies more lenience.
    When no qualifier is given, assume a modest strictness that includes directly related entities like people, places, organizations, and events.

    For any file that you're not sure about, use the 'sample_file' tool to get a better understanding of the file contents.
    If that file does not seem appropriately relevant, do not include it in the output.

    **Output:**
    A bullet list of suggested files.

    Do not add explanations. Output only the files to keep OR the exact completion phrase.
    """,
    tools=[sample_file],
    input_schema=FileSuggestionsInput,
    output_key=STATE_CURRENT_FILES,
)

suggest_import_files_sequence = SequentialAgent(
    name="suggest_import_files",
    description="Executes a sequence of file listing then file criticizing to suggest import files.",
    sub_agents=[initial_file_listing, file_critic],
)

root_agent = suggest_import_files_sequence