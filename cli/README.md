# CLI Tools

A collection of command-line tools for managing your knowledge graph and generating synthetic data.

## Usage

All scripts are located in the `cli/` directory and can be run from the project root using `uv run`. For detailed information on any script, use the `--help` flag.

**Example:**
```bash
uv run cli/csv_to_md.py --help
```

---

## Available Scripts

### `augment_csv.py`

Enriches a CSV file by adding new columns with data generated by an LLM based on a user-provided prompt.

- **Help:** `uv run cli/augment_csv.py --help`

### `copy_to_import.py`

Copies local files and directories into the Neo4j import directory, preserving their structure.

- **Help:** `uv run cli/copy_to_import.py --help`

### `csv_to_md.py`

Converts rows from a CSV file into individual markdown files using a prompt and an LLM.

- **Help:** `uv run cli/csv_to_md.py --help`

### `imitate_csv.py`

Generates a new CSV file with synthetic data that mimics the structure and patterns of a source CSV.

- **Help:** `uv run cli/imitate_csv.py --help`

### `list_import_dir.py`

Lists the contents of the Neo4j import directory, showing files and their relative paths.

- **Help:** `uv run cli/list_import_dir.py --help`

### `one_to_many.py`

Generates multiple synthetic records from a single row of a source CSV file based on a specified field.

- **Help:** `uv run cli/one_to_many.py --help`

### `reset_neo4j.py`

Resets the Neo4j database by deleting all data, constraints, and indexes. **Use with caution.**

- **Help:** `uv run cli/reset_neo4j.py --help`
