
from agentic_kg.sub_agents import unstructured_data_agent
from .common.config import validate_env
# from .coordinators.just_cypher.agent import just_cypher_agent
# from .coordinators.cypher_and_files.agent import cypher_and_files_agent
# from .coordinators.full_workflow.agent import kg_construction_agent

from .sub_agents.unstructured_data_agent.agent import unstructured_data_agent
# Load environmental config and connect to Neo4j
validate_env()

# Instantiate the selected agent
# root_agent = just_cypher_agent
# root_agent = cypher_and_files_agent
# root_agent = kg_construction_agent
root_agent = unstructured_data_agent
