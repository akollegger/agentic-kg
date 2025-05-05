#!/usr/bin/env python3
"""
Augment CSV - Add an LLM-generated field to a CSV file.
"""
import csv
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import click
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def augment_csv_row(row: Dict[str, Any], field_name: str, prompt_template: str, client: OpenAI, model: str = 'gpt-4o-mini') -> Dict[str, Any]:
    """
    Augment a single CSV row with an LLM-generated field.
    
    Args:
        row: The original CSV row as a dictionary
        field_name: Name of the new field to add
        prompt_template: Prompt template to use for generation
        client: OpenAI client instance
        model: OpenAI model to use
        
    Returns:
        Augmented row with the new field
    """
    # Create a copy of the row to avoid modifying the original
    augmented_row = row.copy()
    
    # Convert row to JSON for context
    row_json = json.dumps(row, indent=2)
    
    # Create full prompt with row data as context
    full_prompt = f"{prompt_template}\n\nRow Data:\n{row_json}"
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates field values for CSV data."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        # Extract response
        result = response.choices[0].message.content.strip()
        
        # Add the new field to the row
        augmented_row[field_name] = result
        
    except Exception as e:
        print(f"Error generating field value: {str(e)}")
        # Add empty value if generation fails
        augmented_row[field_name] = ""
    
    return augmented_row

def process_csv_file(
    source_file: Path, 
    field_name: str,
    prompt_template: str, 
    output_file: Path, 
    client: OpenAI, 
    max_rows: Optional[int] = None,
    model: str = 'gpt-4o-mini'
) -> None:
    """
    Process a CSV file and augment each row with an LLM-generated field.
    
    Args:
        source_file: Path to the input CSV file
        field_name: Name of the new field to add
        prompt_template: Prompt template to use for generation
        output_file: Path where the augmented CSV will be saved
        client: OpenAI client instance
        max_rows: Maximum number of rows to process (None for all)
        model: OpenAI model to use
    """
    # Create parent directory for output file if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Read source CSV file
    with open(source_file, 'r', newline='') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames or []
        
        # Check if field already exists
        if field_name in fieldnames:
            raise ValueError(f"Field '{field_name}' already exists in the CSV file")
        
        # Add new field to fieldnames
        new_fieldnames = fieldnames + [field_name]
        
        # Open output file for writing
        with open(output_file, 'w', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=new_fieldnames)
            writer.writeheader()
            
            # Process each row
            for i, row in enumerate(reader):
                if max_rows is not None and i >= max_rows:
                    break
                
                # Augment row with new field
                augmented_row = augment_csv_row(row, field_name, prompt_template, client, model)
                
                # Write augmented row to output file
                writer.writerow(augmented_row)
                
                print(f"Processed row {i+1}, added field '{field_name}'")

@click.command()
@click.option('--source', '-s', type=click.Path(exists=True), required=True,
              help='Source CSV file to augment')
@click.option('--field', '-f', required=True,
              help='Name of the field to add')
@click.option('--prompt-file', type=click.Path(exists=True),
              help='File containing the prompt template to apply to each row')
@click.option('--prompt', '-p',
              help='Prompt template to apply to each row (alternative to --prompt-file)')
@click.option('--out', '-o', type=click.Path(), required=True,
              help='Output CSV file path')
@click.option('--rows', '-n', type=int,
              help='Maximum number of rows to process')
@click.option('--api',
              help='OpenAI API key (overrides environment variables)')
@click.option('--model', '-m', default='gpt-4o-mini',
              help='OpenAI model to use (default: gpt-4o-mini)')
def augment_csv(
    source: str,
    field: str,
    prompt_file: Optional[str],
    prompt: Optional[str],
    out: str,
    rows: Optional[int],
    api: Optional[str],
    model: str
):
    """
    Augment a CSV file with an LLM-generated field.
    
    This tool processes a source CSV file, adds a new field to each row with values
    generated by OpenAI based on the provided prompt, and writes the augmented CSV
    to the specified output file.
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
            "Either --prompt-file or --prompt must be provided."
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
    
    # Process the CSV file
    source_path = Path(source)
    output_path = Path(out)
    
    print(f"Augmenting {source_path.name} with field '{field}'...")
    try:
        process_csv_file(source_path, field, prompt_template, output_path, client, rows, model)
        print(f"Successfully wrote augmented CSV to {output_path}")
    except Exception as e:
        raise click.ClickException(f"Error processing CSV file: {str(e)}")

if __name__ == '__main__':
    augment_csv()
