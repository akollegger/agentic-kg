from .neo4j_interaction import PreparedCypherStatement

echo_message_cypher: PreparedCypherStatement = {
    "query": "RETURN $message as message",
    "expected_params": ["message"]
}

