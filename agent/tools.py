"""
Tool Definitions for the VirtualChef Agent

Defines the Tavily search tool for finding recipes on the web.
"""

from langchain_tavily import TavilySearch

from config import SEARCH_MAX_RESULTS, SEARCH_DEPTH


def get_search_tool():
    """Create and return the Tavily search tool for recipe searches.

    Returns:
        TavilySearch: Configured search tool instance.
    """
    return TavilySearch(
        max_results=SEARCH_MAX_RESULTS,
        search_depth=SEARCH_DEPTH,
        include_raw_content=True,
        name="search_recipes",
        description=(
            "Search the web for recipes based on ingredients. "
            "Use this to find recipes that match the user's available ingredients "
            "and dietary preferences. Returns recipe names, descriptions, and links."
        )
    )


# Defer instantiation so a missing TAVILY_API_KEY at import time doesn't
# crash the Streamlit process before the UI can display a helpful error.
try:
    search_recipes = get_search_tool()
    tools = [search_recipes]
except Exception:  # noqa: BLE001
    search_recipes = None  # type: ignore[assignment]
    tools = []

# Dictionary for quick tool lookup by name
tools_by_name = {tool.name: tool for tool in tools}
