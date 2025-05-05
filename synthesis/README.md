# Synthesis Module

A collection of CLI tools for generating synthetic data based on CSV inputs.

## Overview

This module provides command-line tools for generating synthetic data from CSV files:

### csv_to_md

Converts CSV data to markdown files using OpenAI's language models:

1. Reading rows from one or more CSV files
2. For each row, combining the row data with a prompt template
3. Calling OpenAI's API to generate synthetic content
4. Saving the results as markdown files in an output directory

### imitate_csv

Generates a new CSV file with fake data based on the structure of a source CSV file:

1. Detecting the format and field types of the source CSV
2. Generating appropriate fake data for each field
3. Creating unique IDs based on the source data
4. Writing a new CSV file with the generated data

## Installation

The synthesis module is part of the agentic-kg project. Make sure you have all dependencies installed:

```bash
uv sync
```

## Usage

### csv_to_md

The basic usage pattern is:

```bash
python -m synthesis.csv_to_md [OPTIONS] CSV_FILES...
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
python -m synthesis.csv_to_md data/people.csv --prompt "Generate a detailed biography for this person."
```

### Using a Prompt File

For longer or more complex prompts, use a file:

```bash
python -m synthesis.csv_to_md data/people.csv --prompt-file prompts/biography.txt
```

### Processing Multiple Files

Process multiple CSV files at once:

```bash
python -m synthesis.csv_to_md data/people.csv data/companies.csv --prompt-file prompts/description.txt
```

### Limiting Rows

Process only the first 5 rows of each CSV:

```bash
python -m synthesis.csv_to_md data/people.csv --prompt "Generate a profile." --rows 5
```

### Specifying a Different Model

Use a different OpenAI model:

```bash
python -m synthesis.csv_to_md data/people.csv --prompt "Generate content." --model gpt-4
```

### Custom Output Directory

Save results to a custom directory:

```bash
python -m synthesis.csv_to_md data/people.csv --prompt "Generate content." --output-dir results/generated
```

## Output Format

### csv_to_md

For each CSV file processed, the tool creates a subdirectory in the output directory named after the CSV file (without extension). Within this subdirectory, it creates a markdown file for each row, named `row_N.md` where N is the row number.

## Imitate CSV Tool

### Overview

The `imitate_csv` tool analyzes a source CSV file and generates a new CSV with fake data that follows the same structure and patterns as the original.

### Usage

```bash
python -m synthesis.imitate_csv [OPTIONS]
```

### Options

- `--source PATH`: Source CSV file to imitate (required)
- `--id TEXT`: Field to treat as unique ID
- `--out PATH`: Output CSV file path (required)
- `--rows INTEGER`: Number of rows to generate (default: 10)
- `--help`: Show help message and exit

### Examples

#### Basic Usage

Generate 10 rows of fake data based on a source CSV:

```bash
python -m synthesis.imitate_csv --source data/movies/people.csv --out data/synthetic/fake_people.csv
```

#### Specifying an ID Field

Treat a specific field as a unique ID:

```bash
python -m synthesis.imitate_csv --source data/movies/people.csv --id personId --out data/synthetic/fake_people.csv
```

#### Generating More Rows

Generate 100 rows of fake data:

```bash
python -m synthesis.imitate_csv --source data/movies/people.csv --out data/synthetic/fake_people.csv --rows 100
```

### How It Works

1. The tool uses `clevercsv` to detect the format of the source CSV file
2. It analyzes the data to determine the type of each field (integer, string, email, date, etc.)
3. For each field, it generates appropriate fake data using the `faker` library
4. If an ID field is specified, it ensures unique values are generated
   - For numeric IDs, it starts from a value higher than the maximum in the source file
   - For string IDs, it generates unique values using `nanoid`
5. The generated data is written to the output file with the same structure as the source
