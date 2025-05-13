
from .common.config import load_and_connect
# from .coordinators.just_cypher.agent import just_cypher_agent
from .coordinators.cypher_and_files.agent import cypher_and_files_agent

# Load environmental config and connect to Neo4j
load_and_connect()

# Instantiate the selected agent
# root_agent = just_cypher_agent
root_agent = cypher_and_files_agent

