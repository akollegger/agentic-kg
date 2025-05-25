#!/usr/bin/env python3
"""
Copy to Import - Copy files to the Neo4j import directory.

This tool discovers the Neo4j import directory by connecting to Neo4j
and then copies specified files to that location.
"""
import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import click

from lib.neo4j_utils import get_neo4j_import_directory


USAGE_EXAMPLES = """
Examples:

\b
  # Copy a single file to the Neo4j import directory (flat structure)
  $ python -m cli.copy_to_import data/movies/people.csv

\b 
  # Copy multiple files to the Neo4j import directory
  $ python -m cli.copy_to_import data/movies/people.csv data/movies/movies.csv

\b
  # Copy a file with a new name in the destination
  $ python -m cli.copy_to_import data/movies/people.csv:actors.csv

\b
  # Copy multiple files, including one with a new name
  $ python -m cli.copy_to_import data/movies/people.csv:actors.csv data/movies/movies.csv

\b
  # Copy with verbose output
  $ python -m cli.copy_to_import --verbose data/movies/people.csv

\b
  # Preserve directory structure in the import directory (mirror mode)
  $ python -m cli.copy_to_import --mirror data/movies/some/actors.csv
  # This will create 'data/movies/some/actors.csv' in the import directory

\b
  # Copy an entire directory recursively (preserves directory structure by default)
  $ python -m cli.copy_to_import data/movies/some
  # This will recreate the directory structure in the import directory

\b
  # Flatten directory structure when copying
  $ python -m cli.copy_to_import --flatten data/movies/some
  # This will copy all files to the root of the import directory

\b
  # Clear the import directory before copying
  $ python -m cli.copy_to_import --clear data/movies/some
  # This will remove all existing files in the import directory first
"""


def format_timestamp(timestamp):
    """Convert a timestamp to a human-readable format"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


@click.command(epilog=USAGE_EXAMPLES)
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information about file operations')
@click.option('--flatten', '-f', is_flag=True, help='Flatten directory structure (copy all files to root of import directory)')
@click.option('--clear', '-c', is_flag=True, help='Clear the import directory before copying files')
@click.argument('sources', nargs=-1, required=True, type=str)
def copy_to_import(verbose: bool, flatten: bool, clear: bool, sources: List[str]):
    """
    Copy files or directories to the Neo4j import directory.
    
    This tool behaves like the shell cp command but with the destination
    automatically set to the Neo4j import directory.
    
    SOURCE can be a file or directory path. For files, you can use the format:
    original_path:new_name to rename the file in the destination.
    
    When copying directories, the source directory and its contents are copied to a
    subdirectory with the same name in the import directory by default.
    
    Use --flatten to copy all files directly to the root of the import directory.
    
    When copying directories, all files within the directory will be copied
    recursively.
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
            
        # Clear the import directory if requested
        if clear:
            import_dir_path = Path(import_dir)
            files_removed = 0
            dirs_removed = 0
            
            # Ask for confirmation
            print(f"\nWARNING: You are about to delete all files in {import_dir}")
            confirmation = input("Are you sure you want to proceed? (y/N): ")
            
            if confirmation.lower() != 'y':
                print("Operation cancelled.")
                sys.exit(0)
                
            # Remove all files and directories in the import directory
            for item in import_dir_path.iterdir():
                if item.is_file():
                    item.unlink()
                    files_removed += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    dirs_removed += 1
                    
            print(f"Cleared import directory: {files_removed} files and {dirs_removed} directories removed.")

        
        # Verbose mode is handled during file operations
        
        # Process each source argument
        for source in sources:
            # Check if the source includes a rename using the format path:new_name
            if ':' in source:
                source_path_str, dest_filename = source.split(':', 1)
                rename_mode = True
            else:
                source_path_str = source
                dest_filename = None
                rename_mode = False
            
            # Create Path objects
            source_path = Path(source_path_str)
            
            # Validate source is a relative path
            if source_path.is_absolute():
                print(f"Error: Source must be a relative path: {source_path}")
                continue
                
            # Validate source exists
            if not source_path.exists():
                print(f"Error: Source does not exist: {source_path}")
                continue
            
            # Handle directories and files differently
            if source_path.is_dir():
                if rename_mode:
                    print(f"Error: Cannot rename a directory using ':' syntax: {source_path}")
                    continue
                    
                # Copy directory contents
                files_copied = 0
                for file_path in source_path.glob('**/*'):
                    if file_path.is_file():
                        if flatten:
                            # In flatten mode, just use the filename
                            dest_file_path = Path(import_dir) / file_path.name
                        else:
                            # By default, preserve the source directory structure
                            # Calculate path relative to the source directory's parent
                            if source_path.is_relative_to(Path.cwd()):
                                # If source is relative to CWD, include the source dir name in the path
                                rel_path = file_path.relative_to(source_path.parent)
                            else:
                                # If source is already an absolute path, just use the filename
                                rel_path = file_path.relative_to(source_path)
                                rel_path = Path(source_path.name) / rel_path
                            dest_file_path = Path(import_dir) / rel_path
                        
                        # Create parent directories if they don't exist
                        dest_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy the file
                        shutil.copy2(file_path, dest_file_path)
                        files_copied += 1
                        
                        # Print output if verbose
                        if verbose:
                            print(f"{file_path} -> {dest_file_path}")
                
                # Print summary if not verbose
                if not verbose:
                    print(f"Copied {files_copied} files from directory: {source_path}")
            else:
                # Handle single file copy
                # Determine destination path
                if dest_filename is None:
                    if mirror:
                        # Preserve the relative path structure (mirror mode)
                        destination_path = Path(import_dir) / source_path
                    else:
                        # Flat structure (default mode)
                        destination_path = Path(import_dir) / source_path.name
                else:
                    # When renaming, just use the new filename at the root of import dir
                    destination_path = Path(import_dir) / dest_filename
                    
                # Create parent directories if they don't exist
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                shutil.copy2(source_path, destination_path)
                
                # Print output (cp-style verbose output if verbose flag is set)
                if verbose:
                    print(f"{source_path} -> {destination_path}")
                else:
                    print(f"Copied: {source_path} → {destination_path}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    copy_to_import()
