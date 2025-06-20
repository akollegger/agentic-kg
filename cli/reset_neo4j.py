import argparse
import sys
from rich.console import Console

from agentic_kg.tools.cypher_tools import reset_neo4j_data

console = Console()


def main():
    """
    Deletes all nodes, relationships, constraints, and indexes from the Neo4j database.
    """
    parser = argparse.ArgumentParser(
        description="Deletes all nodes, relationships, constraints, and indexes from the Neo4j database."
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt."
    )
    args = parser.parse_args()

    if not args.yes:
        confirm = input("Are you sure you want to delete everything in the Neo4j database? This action cannot be undone. [y/N] ")
        if confirm.lower() != 'y':
            console.print("[bold yellow]Operation cancelled.[/bold yellow]")
            sys.exit(0)

    console.print("[bold yellow]Resetting Neo4j database...[/bold yellow]")
    result = reset_neo4j_data()

    if result.get("status") == "error":
        console.print(f"[bold red]An error occurred: {result.get('error_message')}[/bold red]")
        sys.exit(1)

    console.print("\n[bold green]Neo4j database has been reset.[/bold green]")


if __name__ == "__main__":
    main()
