from typing import Optional
import json
import arxiv

def search(query: str) -> Optional[str]:
    """
    Fetch research papers from arXiv for a given query and return as JSON.

    Args:
        query (str): The search query string.

    Returns:
        Optional[str]: A JSON string containing the query and search results, or None if no result is found.
    """
    try:
        # Create a client with appropriate parameters
        client = arxiv.Client()
        
        # Create a search query
        search = arxiv.Search(
            query=query,
            max_results=5,  # Limit to 5 results
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        # Get the results
        results = list(client.results(search))
        
        if not results:
            return None
        
        # Format the results
        formatted_results = []
        for paper in results:
            formatted_results.append({
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "summary": paper.summary,
                "published": paper.published.isoformat(),
                "pdf_url": paper.pdf_url,
                "entry_id": paper.entry_id
            })
        
        # Create a dictionary with query and results
        result = {
            "query": query,
            "results": formatted_results
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        print(f"An error occurred while processing the arXiv query: {e}")
        return None


if __name__ == '__main__':
    queries = ["knowledge graph", "transformer neural networks"]
    
    for query in queries:
        result = search(query)
        if result:
            print(f"JSON result for '{query}':\n{result}\n")
        else:
            print(f"No result found for '{query}'\n")
