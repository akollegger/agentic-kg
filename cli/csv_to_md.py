import csv
import json
import re
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import click
from openai import OpenAI
from dotenv import load_dotenv
import os
import nanoid

# Load environment variables from .env file
load_dotenv()

def process_csv_file(csv_file: Path, prompt_template: str, output_dir: Path, client: OpenAI, filename_field: Optional[str] = None, max_rows: Optional[int] = None, model: str = 'gpt-4o-mini') -> None:
    """Process a single CSV file and generate synthetic data for each row.
    
    Args:
        csv_file: Path to the input CSV file
        prompt_template: Prompt template to use for each row
        output_dir: Directory where output markdown files will be saved
        client: OpenAI client instance
    """
    # Create subdirectory for this CSV's output
    file_output_dir = output_dir / csv_file.stem
    file_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read and process CSV file
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if max_rows is not None and i >= max_rows:
                break
            # Create prompt by combining template with row data
            row_json = json.dumps(row, indent=2)
            full_prompt = f"{prompt_template}\n\nRow Data:\n{row_json}"
            
            try:
                # Call OpenAI API
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ]
                )
                
                # Extract response
                result = response.choices[0].message.content
                
                # Generate filename based on the filename_field if provided
                if filename_field and filename_field in row:
                    field_value = row[filename_field]
                    
                    # Check if the field value is numeric
                    try:
                        numeric_value = float(field_value)
                        is_numeric = True
                    except (ValueError, TypeError):
                        is_numeric = False
                    
                    if is_numeric:
                        # For numeric fields, use the source file basename and the numeric value
                        base_name = csv_file.stem
                        filename = f"{base_name}_{int(float(field_value))}.md"
                    else:
                        # For string fields, convert to snake case and add nanoid
                        # Convert to lowercase and replace spaces/special chars with underscores
                        snake_case = re.sub(r'[^\w\s]', '', str(field_value)).lower().replace(' ', '_')
                        # Limit length to avoid extremely long filenames
                        snake_case = snake_case[:30]
                        # Generate a 4-character nanoid
                        unique_id = nanoid.generate(size=4)
                        filename = f"{snake_case}_{unique_id}.md"
                else:
                    # Default naming if no filename field is provided
                    filename = f"row_{i+1}.md"
                
                # Save to markdown file
                output_file = file_output_dir / filename
                with open(output_file, 'w') as f:
                    f.write(result)
                
                print(f"[{csv_file.name}] Processed row {i+1}, saved to {output_file}")
            
            except Exception as e:
                print(f"[{csv_file.name}] Error processing row {i+1}: {str(e)}")

USAGE_EXAMPLES = """

Examples:

\b
  # Process a single CSV file with a prompt file (recommended)
  $ python -m cli.csv_to_md data/movies/people.csv --prompt-file prompts/actor_bio.txt

\b  
  # Use a prompt file and custom output directory
  $ python -m cli.csv_to_md data/movies/people.csv --prompt-file prompts/actor_bio.txt --output-dir results/bios

\b
  # Process multiple CSV files with a limit on rows and custom model
  $ python -m cli.csv_to_md data/movies/people.csv data/movies/movies.csv \\
    --prompt-file prompts/description.txt --rows 5 --model gpt-4o-mini

\b
  # Use a field for naming output files
  $ python -m cli.csv_to_md data/movies/people.csv --prompt-file prompts/actor_bio.txt --filename-field name

\b
  # Inline prompt (alternative to prompt file)
  $ python -m cli.csv_to_md data/movies/people.csv --prompt "Generate a quirky biography."
"""

@click.command(epilog=USAGE_EXAMPLES)
@click.argument('csv_files', type=click.Path(exists=True), nargs=-1, required=True)
@click.option('--prompt-file', '-f', type=click.Path(exists=True), help='File containing the prompt template to apply to each row')
@click.option('--prompt', '-p', help='Prompt template to apply to each row (alternative to --prompt-file)')
@click.option('--output-dir', '-o', type=click.Path(), default='data/synthetic',
              help='Directory where markdown files will be saved (default: data/synthetic)')
@click.option('--rows', '-n', type=int, help='Maximum number of rows to process per file')
@click.option('--api', help='OpenAI API key (overrides environment variables)')
@click.option('--model', '-m', default='gpt-4o-mini', help='OpenAI model to use (default: gpt-4o-mini)')
@click.option('--filename-field', help='CSV field to use for naming output files. For string fields, converts to snake_case with a nanoid. For numeric fields, uses source filename with the numeric value.')
def generate_synthetic_data(csv_files: List[str], prompt_file: str | None, prompt: str | None, output_dir: str, rows: int | None, api: str | None, model: str, filename_field: Optional[str] = None):
    """Generate synthetic data based on CSV input using OpenAI.
    
    Process one or more CSV files, applying the given prompt template to each row
    and generating synthetic data using OpenAI. Results are saved as markdown files
    in the output directory.
    """
    # Determine API key with precedence:
    # 1. Shell environment variable (lowest)
    # 2. .env file (loaded by python-dotenv)
    # 3. --api flag (highest)
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api:
        api_key = api
        
    if not api_key:
        raise click.ClickException(
            "OpenAI API key not found. Please provide it using one of these methods:\n"
            "1. Set OPENAI_API_KEY in your shell environment\n"
            "2. Add OPENAI_API_KEY to your .env file\n"
            "3. Pass it with the --api flag"
        )
        
    # Ensure either prompt or prompt_file is provided
    if not prompt_file and not prompt:
        raise click.ClickException(
            "Either --prompt-file (-f) or --prompt (-p) must be provided."
        )
    
    if prompt_file and prompt:
        click.echo("Both --prompt-file and --prompt provided. Using --prompt-file.")
        
    # Get prompt from file if specified
    prompt_template = prompt
    if prompt_file:
        try:
            with open(prompt_file, 'r') as f:
                prompt_template = f.read().strip()
        except Exception as e:
            raise click.ClickException(f"Error reading prompt file: {str(e)}")
    
    # Initialize OpenAI client with the API key
    client = OpenAI(api_key=api_key)
    
    # Create main output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each CSV file
    for csv_file in csv_files:
        csv_path = Path(csv_file)
        print(f"\nProcessing {csv_path.name}...")
        process_csv_file(csv_path, prompt_template, output_path, client, filename_field, rows, model)

if __name__ == '__main__':
    generate_synthetic_data()
