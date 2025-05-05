# Data Synthesis Module

A CLI tool for generating synthetic data based on CSV inputs using OpenAI's language models.

## Overview

This module provides a command-line interface for processing CSV files and generating synthetic data for each row. It works by:

1. Reading rows from one or more CSV files
2. For each row, combining the row data with a prompt template
3. Calling OpenAI's API to generate synthetic content
4. Saving the results as markdown files in an output directory

## Installation

The data_synthesis module is part of the agentic-kg project. Make sure you have all dependencies installed:

```bash
uv sync
```

## Usage

The basic usage pattern is:

```bash
python -m data_synthesis.cli [OPTIONS] CSV_FILES...
```

### Arguments

- `CSV_FILES`: One or more CSV files to process (required)

### Options

- `-f, --prompt-file PATH`: File containing the prompt template to apply to each row
- `-p, --prompt TEXT`: Prompt template to apply to each row (alternative to --prompt-file)
- `-o, --output-dir PATH`: Directory where markdown files will be saved (default: "data/synthetic")
- `-n, --rows INTEGER`: Maximum number of rows to process per file
- `--api TEXT`: OpenAI API key (overrides environment variables)
- `-m, --model TEXT`: OpenAI model to use (default: "gpt-4o-mini")
- `--help`: Show help message and exit

## API Key Configuration

The tool supports three methods for providing your OpenAI API key, in order of precedence (lowest to highest):

1. Shell environment variable: `export OPENAI_API_KEY=your-key`
2. `.env` file in the project root with `OPENAI_API_KEY=your-key`
3. Command-line flag: `--api your-key`

## Examples

### Basic Usage

Process a single CSV file with an inline prompt:

```bash
python -m data_synthesis.cli data/people.csv --prompt "Generate a detailed biography for this person."
```

### Using a Prompt File

For longer or more complex prompts, use a file:

```bash
python -m data_synthesis.cli data/people.csv --prompt-file prompts/biography.txt
```

### Processing Multiple Files

Process multiple CSV files at once:

```bash
python -m data_synthesis.cli data/people.csv data/companies.csv --prompt-file prompts/description.txt
```

### Limiting Rows

Process only the first 5 rows of each CSV:

```bash
python -m data_synthesis.cli data/people.csv --prompt "Generate a profile." --rows 5
```

### Specifying a Different Model

Use a different OpenAI model:

```bash
python -m data_synthesis.cli data/people.csv --prompt "Generate content." --model gpt-4
```

### Custom Output Directory

Save results to a custom directory:

```bash
python -m data_synthesis.cli data/people.csv --prompt "Generate content." --output-dir results/generated
```

## Output Format

For each CSV file processed, the tool creates a subdirectory in the output directory named after the CSV file (without extension). Within this subdirectory, it creates a markdown file for each row, named `row_N.md` where N is the row number.
