#!/usr/bin/env python3
"""
List Import Files - List files in the Neo4j import directory.

This tool discovers the Neo4j import directory by connecting to Neo4j
and then lists the files at that location.
"""
import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

import click

from lib.neo4j_utils import get_neo4j_import_directory


USAGE_EXAMPLES = """
Examples:

\b
  # List all files in the Neo4j import directory
  $ python -m cli.list_import_dir 

\b
  # Show directory structure as a tree (directories only, like 'tree -d')
  $ python -m cli.list_import_dir --tree

\b
  # Show all files in tree format
  $ python -m cli.list_import_dir --tree --all

\b
  # Show tree with detailed information
  $ python -m cli.list_import_dir --tree --long

"""


def format_timestamp(timestamp: float) -> str:
    """Convert a timestamp to a human-readable format"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def build_directory_tree(root_path: Path, show_files: bool = False) -> Dict[str, Any]:
    """Build a nested dictionary representing the directory structure."""
    tree = {"name": root_path.name, "is_dir": True, "children": []}
    
    try:
        for entry in sorted(os.scandir(root_path), key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.is_dir():
                tree["children"].append(build_directory_tree(Path(entry.path), show_files))
            elif show_files and entry.is_file():
                tree["children"].append({"name": entry.name, "is_dir": False})
    except (PermissionError, OSError):
        pass
        
    return tree


def print_tree(node: Dict[str, Any], prefix: str = "", is_last: bool = True, 
               show_timestamps: bool = False) -> None:
    """Print the directory tree structure."""
    # Print the current node
    if node["name"]:  # Skip empty root name for the top level
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node['name']}")
    
    # Update prefix for children
    if is_last:
        new_prefix = f"{prefix}    "
    else:
        new_prefix = f"{prefix}│   "
    
    # Print children
    if "children" in node:
        children = node["children"]
        for i, child in enumerate(children):
            print_tree(child, new_prefix, i == len(children) - 1, show_timestamps)


@click.command(epilog=USAGE_EXAMPLES)
@click.option('--long', '-l', is_flag=True, help='Use a long listing format')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information about file operations')
@click.option('--tree', '-t', is_flag=True, help='Display directory structure as a tree')
@click.option('--all', '-a', 'show_all', is_flag=True, help='Show all files in tree view (implies --tree)')
def list_import_dir(long: bool, verbose: bool, tree: bool, show_all: bool):
    """
    List files in the Neo4j import directory.
    
    This tool behaves like the shell `ls` command but with the destination
    automatically set to the Neo4j import directory.    
    """
    try:
        # Get the Neo4j import directory
        try:
            import_dir = get_neo4j_import_directory()
            if verbose:print(f"Neo4j import directory: \"{import_dir}\"")
        except ValueError as e:
            error_message = str(e)
            print(f"Error: {error_message}")
            
            # Check for specific error about remote Neo4j instance
            if "does not exist on this machine" in error_message:
                print("Attempted to find Neo4j import directory for server running at:", os.environ.get('NEO4J_URI'))
                print("Ensure you are connecting to a local Neo4j instance, not a remote one")
            else:
                print("\nPlease ensure the following environment variables are set:")
                print("  NEO4J_URI - The URI of your Neo4j instance (e.g., neo4j://localhost:7687)")
                print("  NEO4J_USERNAME - Your Neo4j username (default: neo4j)")
                print("  NEO4J_PASSWORD - Your Neo4j password")
                print("  NEO4J_DATABASE - Your Neo4j database name (optional)")
            
            sys.exit(1)
            
        try:
            import_path = Path(import_dir)
            
            if tree or show_all:
                # Tree view requested
                if not import_path.exists():
                    print(f"Error: Directory does not exist: {import_path}", file=sys.stderr)
                    sys.exit(1)
                
                if verbose:
                    print(f"Scanning directory: {import_path}", file=sys.stderr)
                
                # Build and print the tree
                tree_data = build_directory_tree(import_path, show_all)
                print_tree(tree_data, show_timestamps=long)
            else:
                # Original list view
                entries = []
                with os.scandir(import_dir) as it:
                    for entry in it:
                        try:
                            entries.append((entry.name, entry.is_dir(), entry.stat().st_mtime))
                        except (OSError, PermissionError) as e:
                            if verbose:
                                print(f"Error accessing {entry.name}: {e}", file=sys.stderr)
                
                # Sort directories first, then by name
                entries.sort(key=lambda x: (not x[1], x[0].lower()))
                
                if long:
                    # Long format: show details like ls -l
                    for name, is_dir, mtime in entries:
                        time_str = format_timestamp(mtime)
                        dir_indicator = "/" if is_dir else ""
                        print(f"{time_str} {name}{dir_indicator}")
                else:
                    # Simple format: just names like ls
                    for name, is_dir, _ in entries:
                        print(f"{name}{'/' if is_dir else ''}")
                
        except OSError as e:
            print(f"Error reading import directory: {e}", file=sys.stderr)
            sys.exit(1)


            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    list_import_dir()
