import csv
import json
from pathlib import Path
import click
from openai import OpenAI

@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.argument('prompt_template', type=str)
@click.argument('output_dir', type=click.Path())
def generate_synthetic_data(csv_file, prompt_template, output_dir):
    """Generate synthetic data based on CSV input using OpenAI.
    
    Args:
        csv_file: Path to the input CSV file
        prompt_template: Prompt template to use for each row
        output_dir: Directory where output markdown files will be saved
    """
    # Initialize OpenAI client
    client = OpenAI()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read and process CSV file
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Create prompt by combining template with row data
            row_json = json.dumps(row, indent=2)
            full_prompt = f"{prompt_template}\n\nRow Data:\n{row_json}"
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            # Extract response
            result = response.choices[0].message.content
            
            # Save to markdown file
            output_file = output_path / f"row_{i+1}.md"
            with open(output_file, 'w') as f:
                f.write(result)
            
            print(f"Processed row {i+1}, saved to {output_file}")

if __name__ == '__main__':
    generate_synthetic_data()