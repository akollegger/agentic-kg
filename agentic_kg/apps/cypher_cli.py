import os

from graph_intelligence.tools.neo4j.neo4j_interaction import prepare_interaction
from neo4j import GraphDatabase

# Load environment variables and set up driver configuration    
from dotenv import load_dotenv
load_dotenv()
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

import sys

def run():
    # Initialize the driver
    driver = GraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_username, neo4j_password)
    )

    # Prepare a cypher interaction environment
    interact = prepare_interaction(
        driver,
        "neo4j"
    )

    # Handle command-line arguments as Cypher queries
    args = sys.argv[1:]
    if not args:
        print("Usage: uv run -m graph_intelligence.apps.cypher_cli <CYPHER_QUERY_1> [<CYPHER_QUERY_2> ...]")
        driver.close()
        return
    for query in args:
        result = interact(query)
        print(result)

    # Close the driver
    driver.close()

if __name__ == "__main__":
    run()
    