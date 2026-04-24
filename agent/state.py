"""
State Schema for the VirtualChef Agent

Defines the state structure using TypedDict with proper reducers
following LangGraph v1 patterns.
"""

from typing import Annotated, List
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
import operator


class ChefState(TypedDict):
    """State schema for the AI Chef agent.

    Attributes:
        messages: Conversation history with add reducer.
                  New messages are appended to existing list.
        ingredients: List of ingredients the user has available.
        dietary_preferences: Any dietary restrictions or preferences
                            as a comma-separated string.
        max_cooking_time: Maximum cooking time in minutes.
    """
    messages: Annotated[List[AnyMessage], operator.add]
    ingredients: List[str]
    dietary_preferences: str
    max_cooking_time: int
