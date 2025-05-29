
from .common.config import validate_env



# Load environmental config and connect to Neo4j
validate_env()

# Import and instantiate only one agent (comment out the rest)

## just cypher - a single agent that can read/write arbitrary cypher
# Agents:
#   - coordinators/just_cypher/agent
#   - coordinators/just_cypher/sub_agents/cypher_agent
# from .coordinators.just_cypher.agent import cypher_agent
# root_agent = cypher_agent

## cypher and files - a single agent that can read/write arbitrary cypher and files
# Agents:
#   - coordinators/cypher_and_files.agent 
#   - coordinators/cypher_and_files/sub_agents/dataprep_agent 
#   - coordinators/cypher_and_files/sub_agents/cypher_agent 
# from .coordinators.cypher_and_files.agent import cypher_and_files_agent
# root_agent = cypher_and_files_agent

## full workflow - full multi-agent system
# Agents:
#   - coordinators/full_workflow.agent as `full_workflow_agent_v1`
#   - coordinators/full_workflow/sub_agents/file_suggestion_agent.agent as `file_suggestion_agent_v1`
#   - coordinators/full_workflow/sub_agents/schema_suggestion_agent.agent as `schema_suggestion_agent_v1`
#   - sub_agents/cypher_agent as `cypher_agent_v1`
# from .coordinators.full_workflow.agent import full_workflow_agent
# root_agent = full_workflow_agent

from .sub_agents.unstructured_data_agent.agent import unstructured_data_agent
root_agent = unstructured_data_agent
