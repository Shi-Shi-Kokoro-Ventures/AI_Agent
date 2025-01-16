# agent/tools/search_tools.py

from langchain.utilities import GoogleSearchAPIWrapper

def google_search(query: str) -> str:
    """
    Executes a Google search and returns summarized results.
    Requires valid Google API key + CSE ID in environment variables.
    """
    search = GoogleSearchAPIWrapper()
    return search.run(query)
