


## Setup

```bash
uv venv
uv sync
```

Prepare environment vars:
- `cp .env.template .env`
- update `.env` with your values

## Running

```bash
adk run agentic_kg
```

### cypher agent

Instructions to try the cypher-agent:

- `Check the Neo4j connection` should prompt the agent to use the cypher sub-agent to check the connection to Neo4j
- `What's in the graph?` should use the cypher subagent to get the physical schema of the graph (what node labels and relationship types exist)
- `Create a message node with text 'hello world!'` should use the cypher subagent to create a node
- `List messages` should use the cypher subagent to find all nodes with label 'Message'
- `Delete all messages` should use the cypher subagent to delete all nodes with label 'Message'

### data-prep agent

- `what files are available for import?` should use the file subagent to list files in the import directory
- `what is in the people file?` should use the file subagent to sample the people file
- `sample the other files` should prompt the subagent to sample each file in the import directory
