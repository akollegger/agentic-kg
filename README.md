# Agentic KG

A multi-agent project for knowledge graph construction.

## Design Philosophy

This project is primarily **instructional** in nature. It aims to teach the fundamentals of building a multi-agent system that can construct a knowledge graph from CSV and markdown files. The design prioritizes:

- **Simplicity over comprehensiveness**: We make simplifying assumptions where appropriate to keep the code clear and approachable.
- **Educational value**: Each component should demonstrate a concept clearly rather than trying to handle every edge case.
- **Practical examples**: The system should provide working examples that can be extended by learners.

## Learning Goals
- Multi-agent development workflow
- Agent specialization, encapsulating domain expertise
- Knowledge graph construction from structured and semi-structured data

## Project Structure

The project has multiple agents, at two levels:

1. coordinators are root-agents that frame the context for interaction
2. sub_agents are specialized agents with tools

- `src/agentic_kg` is the top-level module
  - initializes the environment
  - specifies which coordinator to use as root-agent
- `src/coordinators` is a collection of root-agents
  - high-level context in the prompt
  - coordinates sub-agents to do things
- `src/sub_agents` specialized agents (some with custom tools)
- `src/tools` for tools that any agent can use

## Setup

```bash
uv venv
uv sync
```

**NOTE**:Don't forget to source the venv, for example: `source .venv/bin/activate`

Prepare environment vars:
- `cp .env.template .env`
- update `.env` with your values

## Running

CLI:
```bash
adk run src/agentic_kg
```

web:
```bash
adk web src
```

Test:
```bash
uv run pytest
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
