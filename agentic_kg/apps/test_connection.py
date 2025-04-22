import os

from typing import Callable, Tuple, List, Dict, Any

from graph_intelligence.tools.neo4j.neo4j_interaction import prepare_interaction
from graph_intelligence.tools.neo4j.result_transformers import result_to_dict
from graph_intelligence.tools.neo4j.cypher_info import echo_message_cypher
from neo4j import GraphDatabase

# Load environment variables and set up driver configuration    
from dotenv import load_dotenv
load_dotenv()
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

def run():
    # Initialize the driver
    driver = GraphDatabase.driver(
        neo4j_uri,
        auth=(neo4j_username, neo4j_password)
    )

    # Create a cypher prepared statement function
    prepare_cypher = prepare_interaction(
        driver,
        "neo4j",
        result_to_dict
    )

    # Prepare a function to test the connection
    test_connection = prepare_cypher(echo_message_cypher["query"])

    # Run it
    result, error = test_connection({"message":"Neo4j is ready."})

    if error:
        print(error)
    else:
        print(result)

    # Close the driver
    driver.close()

if __name__ == "__main__":
    run()
    