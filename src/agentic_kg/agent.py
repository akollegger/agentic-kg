
from .common.config import validate_env



# Load environmental config and connect to Neo4j
validate_env()

# Import and instantiate only one agent (comment out the rest)

## just cypher - a single agent that can read/write arbitrary cypher
# Agents:
#   - sub_agents/cypher_agent as `cypher_root_agent`
from .sub_agents import cypher_agent
root_agent = cypher_agent

## cypher and files - a single agent that can read/write arbitrary cypher and files
# Agents:
#   - coordinators/cypher_and_files.agent as `cypher_and_files_agent`
#   - sub_agents/dataprep_agent as `dataprep_agent_v1`
#   - sub_agents/cypher_agent as `cypher_agent_v1`
# from .coordinators.cypher_and_files.agent import cypher_and_files_agent
# root_agent = cypher_and_files_agent

# from .coordinators.full_workflow.agent import kg_construction_agent
# root_agent = kg_construction_agent

# from .sub_agents.unstructured_data_agent.agent import unstructured_data_agent
# root_agent = unstructured_data_agent
