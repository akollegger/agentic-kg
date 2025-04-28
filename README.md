

## Dev notes

### Setup

```bash
uv venv
uv sync
```

Prepare environment vars:
- `cp .env.template .env`
- update `.env` with your values

### Running

```bash
adk run agentic_kg
```

Instructions to try:

- `Is Neo4j ready?` should prompt the agent to use the cypher sub-agent to check the connection to Neo4j
- `What's in the graph?` should use the cypher subagent to get the physical schema of the graph (what node labels and relationship types exist)
- `Create a node with label 'Person' and property 'name'` should use the cypher subagent to create a node
- `Find all nodes with label 'Person'` should use the cypher subagent to find all nodes with label 'Person'
- `Delete all nodes with label 'Person'` should use the cypher subagent to delete all nodes with label 'Person'


