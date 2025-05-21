"""
Planning module for the graph plan system.

This module contains helper functions for creating and managing graph plans,
following the process described in the README.md file.
"""

import os
import csv
import mimetypes
from typing import List, Optional

from .file_source import FileSource
from .entity_plan import EntityPlan
from .relation_plan import RelationPlan
from .graph_plan import GraphPlan


def file_source_from_file(file_path: str) -> FileSource:
    """Create a FileSource object from a file.
    
    This function analyzes a file and creates a FileSource object with
    appropriate metadata. For CSV files, it extracts the header.
    
    Args:
        file_path: Path to the file
        
    Returns:
        A FileSource object representing the file
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # Default to text/plain if we can't determine the MIME type
        mime_type = "text/plain"
    
    # For CSV files, extract header
    header = []
    if mime_type == "text/csv" or file_path.endswith('.csv'):
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
        except Exception as e:
            # If we can't read the CSV header, log the error but continue
            print(f"Warning: Could not read CSV header from {file_path}: {e}")
    
    return FileSource(
        file_path=file_path,
        mime_type=mime_type,
        header=header
    )


def create_initial_graph_plan(name: str, description: str, file_paths: List[str]) -> GraphPlan:
    """Create an initial graph plan from a list of file paths.
    
    This function creates a graph plan with the given name and description,
    and adds file sources for each file path.
    
    Args:
        name: Name of the graph plan
        description: Description of the graph plan
        file_paths: List of file paths to include in the graph plan
        
    Returns:
        A new GraphPlan instance
    """
    graph_plan = GraphPlan(
        name=name,
        description=description
    )
    
    # Add file sources
    for file_path in file_paths:
        try:
            source = file_source_from_file(file_path)
            graph_plan.sources[source.file_path] = source
        except FileNotFoundError:
            print(f"Warning: File not found: {file_path}")
    
    return graph_plan
