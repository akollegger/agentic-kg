# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Setup:**
```bash
uv venv
uv sync
cp .env.template .env
# Update .env with your API keys and Neo4j credentials
```

**Running the Application:**
```bash
# CLI mode
adk run src/agentic_kg

# Web interface  
adk web src
```

**Testing:**
```bash
# Install dev dependencies
uv sync --group dev

# Run all tests
uv run pytest

# Run specific test modules
uv run pytest src/agentic_kg/common/graph_plan/tests/
uv run python src/agentic_kg/hand_coded/test_persistence.py
```

## Architecture Overview

This is a multi-agent system for knowledge graph construction using Neo4j. The architecture has two main levels:

**Coordinators** (`src/agentic_kg/coordinators/`): Root-level agents that frame context and coordinate sub-agents
- `cypher_and_files/`: Handles Neo4j operations and file management
- `just_cypher/`: Focuses only on Cypher queries
- `full_workflow/`: End-to-end KG construction workflow

**Sub-agents** (`src/agentic_kg/sub_agents/`): Specialized agents with domain expertise
- `cypher_agent/`: Neo4j database operations and Cypher queries
- `dataprep_agent/`: File analysis and data preparation
- `unstructured_data_agent/`: Processing unstructured data sources

**Key Components:**
- `src/agentic_kg/agent.py`: Entry point that selects which coordinator to use as root agent
- `src/agentic_kg/common/graph_plan/`: Declarative structure for KG construction from data files
- `src/agentic_kg/tools/`: Shared tools across agents (file operations, user goals)

## Configuration

**Environment Variables Required:**
- `OPENAI_API_KEY`: For LLM operations
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`: Neo4j connection
- `DATA_DIR`: Directory containing data files for import

**Agent Selection:**
The active root agent is configured in `src/agentic_kg/agent.py`. Currently defaults to `cypher_and_files_agent`.

## Graph Plan Workflow

The system uses a three-phase approach for KG construction:

1. **Identify Data Sources**: Analyze files to determine relevance to user goals
2. **Design Data Model**: Create entity/relationship plans with construction rules  
3. **Construct Knowledge Graph**: Execute the plan to build the graph

The `graph_plan` module provides the core abstractions for this declarative approach to KG construction.