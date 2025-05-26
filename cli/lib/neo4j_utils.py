"""
Neo4j utility functions for CLI tools.
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from .env file
dotenv_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / '.env'
load_dotenv(dotenv_path=dotenv_path)


def load_neo4j_env() -> Dict[str, Any]:
    """
    Load Neo4j connection settings from environment variables.
    
    Returns:
        Dictionary containing Neo4j connection settings
    """
    return {
        "neo4j_uri": os.getenv("NEO4J_URI"),
        "neo4j_username": os.getenv("NEO4J_USERNAME") or "neo4j",
        "neo4j_password": os.getenv("NEO4J_PASSWORD"),
        "neo4j_database": os.getenv("NEO4J_DATABASE") or os.getenv("NEO4J_USERNAME") or "neo4j"
    }


def get_neo4j_import_directory() -> str:
    """
    Queries Neo4j to find the location of the server's import directory,
    which is where files need to be located in order to be used by LOAD CSV.
    
    Returns:
        The path to the Neo4j import directory
        
    Raises:
        ValueError: If the import directory cannot be found or does not exist
    """
    import os.path
    
    # Load Neo4j connection settings from environment variables
    neo4j_settings = load_neo4j_env()
    
    # Validate settings
    if not neo4j_settings["neo4j_uri"]:
        raise ValueError("NEO4J_URI environment variable is not set")
    if not neo4j_settings["neo4j_password"]:
        raise ValueError("NEO4J_PASSWORD environment variable is not set")
    
    # Create a Neo4j driver
    driver = GraphDatabase.driver(
        neo4j_settings["neo4j_uri"],
        auth=(neo4j_settings["neo4j_username"], neo4j_settings["neo4j_password"])
    )
    
    # Query to find the import directory
    find_neo4j_import_dir_cypher = """
    CALL dbms.listConfig() YIELD name, value
    WHERE name CONTAINS 'server.directories.import'
    RETURN value as import_dir
    """
    
    try:
        with driver.session(database=neo4j_settings["neo4j_database"]) as session:
            result = session.run(find_neo4j_import_dir_cypher)
            record = result.single()
            if record is None:
                raise ValueError("Could not find Neo4j import directory")
            import_dir = record["import_dir"]
            
            # Sanity check: verify the directory exists
            if not os.path.isdir(import_dir):
                raise ValueError(
                    f"Neo4j reported import directory '{import_dir}' but it does not exist on this machine. "
                    f"This may indicate you are connecting to a remote Neo4j instance."
                )
                
            return import_dir
    finally:
        driver.close()
