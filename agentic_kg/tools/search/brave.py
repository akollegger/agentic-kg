from typing import Optional
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search(query: str) -> Optional[str]:
    """
    Fetch search results from Brave Search API for a given query and return as JSON.

    Args:
        query (str): The search query string.

    Returns:
        Optional[str]: A JSON string containing the query and search results, or None if no result is found.
    """
    # Get API key from environment variables
    api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        print("Error: BRAVE_API_KEY not found in environment variables")
        return None
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": query,
        "count": 5  # Limit to 5 results
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Create a dictionary with query and results
        result = {
            "query": query,
            "results": data.get("web", {}).get("results", [])
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while processing the Brave search query: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == '__main__':
    queries = ["knowledge graph", "artificial intelligence"]
    
    for query in queries:
        result = search(query)
        if result:
            print(f"JSON result for '{query}':\n{result}\n")
        else:
            print(f"No result found for '{query}'\n")
