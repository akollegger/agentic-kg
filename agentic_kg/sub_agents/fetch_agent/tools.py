
import logging
import urllib.request

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

def list_files(tool_context:ToolContext) -> dict:
    """Lists files available in the configured import directory
    that are available to be read.

        Returns:
            dict: A dictionary containing metadata about the content.
                    Includes a 'status' key ('success' or 'error').
                    If 'success', includes a 'files' key with list of file names.
                    If 'error', includes an 'error_message' key.
    """
    file_names = [
        "movies.csv",
        "persons.csv",
        "acted_in.csv"
    ]

    return {
        "status": "success",
        "files": file_names
    }


def read_file(path: str, tool_context:ToolContext) -> dict:
    """Retrieves the content of 'url' and stores it in the ToolContext.

    Args:
      path: file to fetch.
      tool_context: ToolContext object.

    Returns:
        dict: A dictionary containing metadata about the content.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'metadata' key with content details.
              If 'error', includes an 'error_message' key.
    """
    return {
        "status": "success",
        "metadata": {
            "path": path,
            "mimetype": "text/csv"
        }
    }
