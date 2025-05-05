#!/usr/bin/env python3
"""
Imitate CSV - Generate fake data based on an example CSV file.
"""
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

import click
import clevercsv
import pandas as pd

# Import utility functions from lib.imitate
from data_synthesis.lib.imitate import (
    detect_field_types,
    generate_fake_data
)



@click.command()
@click.option('--source', required=True, type=click.Path(exists=True),
              help='Source CSV file to imitate')
@click.option('--id', 'id_field', help='Field to treat as unique ID')
@click.option('--out', required=True, type=click.Path(),
              help='Output CSV file path')
@click.option('--rows', type=int, default=10,
              help='Number of rows to generate (default: 10)')
def imitate_csv(source: str, id_field: Optional[str], out: str, rows: int):
    """
    Generate a new CSV file with fake data based on the structure of a source CSV file.
    """
    source_path = Path(source)
    output_path = Path(out)
    
    click.echo(f"Reading source file: {source_path}")
    
    try:
        try:
            # Try using pandas to read the CSV which is more robust
            df = pd.read_csv(source_path)
            source_data = df.to_dict('records')
            fieldnames = df.columns.tolist()
        except Exception as e:
            click.echo(f"Pandas read failed: {str(e)}, trying clevercsv...")
            try:
                # Fallback to clevercsv
                with open(source_path, 'r', newline='') as f:
                    # Use standard csv module with auto-detection
                    sample = f.read(4096)
                f.close()
                
                dialect = csv.Sniffer().sniff(sample)
                with open(source_path, 'r', newline='') as f:
                    reader = csv.DictReader(f, dialect=dialect)
                    source_data = list(reader)
                    fieldnames = reader.fieldnames
            except Exception as e2:
                # Last resort: try with default dialect
                click.echo(f"Dialect detection failed: {str(e2)}, using default dialect")
                with open(source_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    source_data = list(reader)
                    fieldnames = reader.fieldnames
            
            if not source_data:
                click.echo("Error: Source file is empty or has no valid rows", err=True)
                sys.exit(1)
                
            # fieldnames already set in the try-except block above
            
            if id_field and id_field not in fieldnames:
                click.echo(f"Error: ID field '{id_field}' not found in source file", err=True)
                sys.exit(1)
        
        # Detect field types with context awareness
        field_types = detect_field_types(source_data, source_path=source_path)
        click.echo(f"Detected {len(field_types)} fields with types:")
        for field, field_type_info in field_types.items():
            # Check specifically for multi-value fields
            if field_type_info.get('type') == 'multi-value':
                click.echo(f"  - {field}: {field_type_info['type']} (separator: '{field_type_info['separator']}', "
                          f"enumerated: {field_type_info.get('is_enumerated', False)}, "
                          f"values: {field_type_info.get('values', [])[:5]}{'...' if len(field_type_info.get('values', [])) > 5 else ''})")
            else:
                # Show context if available
                context_info = ""
                if field_type_info.get('context'):
                    context_info = f", context: {field_type_info.get('context')}"
                click.echo(f"  - {field}: {field_type_info}{context_info}")
        
        # Generate fake data
        click.echo(f"Generating {rows} rows of fake data...")
        fake_data = generate_fake_data(source_data, field_types, id_field, rows, source_path=source_path)
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to output file
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(fake_data)
        
        click.echo(f"Successfully wrote {rows} rows to {output_path}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    imitate_csv()
