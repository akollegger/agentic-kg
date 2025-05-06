#!/usr/bin/env python3
"""
One-to-Many CLI Tool
--------------------
Randomly assign 3-5 (default) relationships from a 'one' CSV file to a 'many' CSV file.

Examples:
  $ python -m cli.one_to_many --one data/social/movie_fans.csv \
    --many data/movies/recent_movies.csv --one-key username --many-key movie_id \
    --out data/social/relationships.csv

  $ python -m cli.one_to_many --one one.csv --many many.csv \
    --one-key id --many-key mid --out relationships.csv --min 4 --max 5 --seed 42
"""
import csv
import random
from pathlib import Path
import click

USAGE_EXAMPLES = """
Examples:

\b
  # Basic usage
  $ python -m cli.one_to_many --one data/social/movie_fans.csv \
    --many data/movies/recent_movies.csv --one-key username --many-key movie_id \
    --out data/social/relationships.csv

\b
  # With a fixed number of associations and reproducibility
  $ python -m cli.one_to_many --one one.csv --many many.csv \
    --one-key id --many-key mid --out relationships.csv --min 4 --max 4 --seed 42
"""

@click.command(epilog=USAGE_EXAMPLES)
@click.option('--one', required=True, type=click.Path(exists=True), help="Path to 'one' CSV file.")
@click.option('--many', required=True, type=click.Path(exists=True), help="Path to 'many' CSV file.")
@click.option('--one-key', required=True, help="Unique ID column in 'one' file.")
@click.option('--many-key', required=True, help="Unique ID column in 'many' file.")
@click.option('--out', required=True, type=click.Path(), help="Output relationships CSV file.")
@click.option('--min', 'min_n', type=int, default=3, show_default=True, help="Minimum associations per 'one'.")
@click.option('--max', 'max_n', type=int, default=5, show_default=True, help="Maximum associations per 'one'.")
@click.option('--seed', type=int, default=None, help="Random seed.")
@click.option('--one-fields', default='', help="Comma-separated list of additional field names from the 'one' file to include in output.")
@click.option('--many-fields', default='', help="Comma-separated list of additional field names from the 'many' file to include in output.")
def one_to_many(one, many, one_key, many_key, out, min_n, max_n, seed, one_fields, many_fields):
    """
    Create a relationships CSV pairing each row in the 'one' file to 3-5 (random) rows in the 'many' file.
    """
    if seed is not None:
        random.seed(seed)

    one_path = Path(one)
    many_path = Path(many)
    out_path = Path(out)

    click.echo(f"Reading 'one' file: {one_path}")
    with open(one_path, newline='', encoding='utf-8') as f:
        one_reader = csv.DictReader(f)
        one_rows = list(one_reader)
        if one_key not in one_reader.fieldnames:
            click.echo(f"Error: Column '{one_key}' not found in 'one' CSV.", err=True)
            return

    click.echo(f"Reading 'many' file: {many_path}")
    with open(many_path, newline='', encoding='utf-8') as f:
        many_reader = csv.DictReader(f)
        many_rows = list(many_reader)
        if many_key not in many_reader.fieldnames:
            click.echo(f"Error: Column '{many_key}' not found in 'many' CSV.", err=True)
            return

    # Parse extra fields from the 'one' file
    one_extra_fields = [f.strip() for f in one_fields.split(',') if f.strip()]
    for ef in one_extra_fields:
        if ef and ef not in one_rows[0]:
            click.echo(f"Warning: Field '{ef}' not found in 'one' CSV; it will be empty in output.", err=True)

    # Parse extra fields from the 'many' file
    many_extra_fields = [f.strip() for f in many_fields.split(',') if f.strip()]
    for ef in many_extra_fields:
        if ef and ef not in many_rows[0]:
            click.echo(f"Warning: Field '{ef}' not found in 'many' CSV; it will be empty in output.", err=True)

    # Prepare header
    header = [one_key, many_key] + one_extra_fields + many_extra_fields
    click.echo(f"Writing relationships to: {out_path}")
    with open(out_path, 'w', newline='', encoding='utf-8') as outf:
        writer = csv.writer(outf)
        writer.writerow(header)
        for one_row in one_rows:
            n = random.randint(min_n, max_n)
            chosen_many = random.sample(many_rows, n)
            for many_row in chosen_many:
                row = [one_row[one_key], many_row[many_key]]
                row += [one_row.get(f, '') for f in one_extra_fields]
                row += [many_row.get(f, '') for f in many_extra_fields]
                writer.writerow(row)

    click.echo(f"Done! {len(one_rows)} 'one' rows processed.")

if __name__ == '__main__':
    one_to_many()
