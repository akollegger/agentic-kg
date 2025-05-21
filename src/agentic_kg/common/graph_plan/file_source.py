"""
File source module for the graph plan system.

This module contains the FileSource class which represents a file that has been analyzed
and prepared for import into a knowledge graph.
"""

from typing import List, Optional
from pydantic import BaseModel


class FileSource(BaseModel):
    """Represents a file source which has been prepared and analyzed for import.
    
    Attributes:
        file_path: The path to the file
        mime_type: The MIME type of the file
        header: The column names of the file, if it is a CSV file
    """
    file_path: str
    mime_type: str
    header: Optional[List[str]] = None

    def __str__(self):
        return f"FileSource(file_path={self.file_path}, mime_type={self.mime_type}, header={self.header})"
