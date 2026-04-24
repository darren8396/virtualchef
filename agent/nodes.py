"""
Node Functions for the VirtualChef Agent

Defines the node functions used in the LangGraph workflow:
- llm_call: Processes user input and generates responses
- tool_node: Executes tool calls from the LLM
- should_continue: Determines workflow routing
"""

from functools import lru_cache
from typing import Literal, List
from langchain_core.messages import SystemMessage, ToolMessage, AnyMessage

from config import MAX_MESSAGE_HISTORY, logger
from .state import ChefState
from .model import get_model
from .tools import tools, tools_by_name


# System prompt that defines the chef's personality and behavior
CHEF_SYSTEM_PROMPT = """You are an expert AI Chef assistant. Your role is to help users find delicious recipes based on the ingredients they have available.

When a user tells you what ingredients they have:
1. Acknowledge the ingredients they mentioned
2. Use the search_recipes tool to find suitable recipes
3. Present 3-5 recipe options with:
   - Recipe name
   - Brief description
   - Key ingredients needed (highlighting what they already have)
   - Estimated cooking time
   - A link to the full recipe if available

Be friendly, encouraging, and creative with your suggestions. If they're missing key ingredients, suggest simple substitutions.

If the user has dietary restrictions, always respect them when searching for recipes.

When searching for recipes:
- Include the main ingredients in your search query
- Add any dietary preferences to filter results
- Look for recipes that maximize the use of available ingredients

Remember to be conversational and helpful. If the user asks follow-up questions about a recipe, provide detailed cooking tips and advice."""


@lru_cache(maxsize=1)
def _get_model_with_tools():
    """Get or create the model with tools bound.
    
    Uses lru_cache to ensure only one instance is created,
    avoiding global mutable state.
    """
    return get_model().bind_tools(tools)


def _truncate_messages(messages: List[AnyMessage]) -> List[AnyMessage]:
    """Truncate message history to prevent excessive token usage.
    
    Keeps the most recent messages up to MAX_MESSAGE_HISTORY.
    Always preserves tool call/response pairs to maintain context.
    
    Args:
        messages: Full list of messages.
        
    Returns:
        Truncated list of messages.
    """
    if len(messages) <= MAX_MESSAGE_HISTORY:
        return messages
    
    # Keep the most recent messages
    truncated = messages[-MAX_MESSAGE_HISTORY:]
    logger.info(f"Truncated message history from {len(messages)} to {len(truncated)} messages")
    return truncated


def llm_call(state: ChefState) -> dict:
    """Call the LLM to process user input and decide on actions.
    
    Args:
        state: Current agent state containing messages and context.
        
    Returns:
        Dictionary with new messages to append to state.
    """
    model_with_tools = _get_model_with_tools()
    
    # Truncate message history to control token usage
    truncated_messages = _truncate_messages(state["messages"])
    
    # Build message list with system prompt
    messages = [
        SystemMessage(content=CHEF_SYSTEM_PROMPT)
    ] + truncated_messages
    
    # Add context about dietary preferences and cooking time if present
    context_parts = []
    if state.get("dietary_preferences"):
        context_parts.append(f"Dietary preferences: {state['dietary_preferences']}")
    if state.get("max_cooking_time"):
        context_parts.append(f"Maximum cooking time: {state['max_cooking_time']} minutes")

    if context_parts:
        context_msg = SystemMessage(
            content=f"User's preferences - {'. '.join(context_parts)}. Please filter recipe suggestions accordingly."
        )
        messages.insert(1, context_msg)
    
    # Invoke the model
    response = model_with_tools.invoke(messages)
    
    return {"messages": [response]}


def tool_node(state: ChefState) -> dict:
    """Execute tool calls made by the LLM.
    
    Args:
        state: Current agent state with pending tool calls.
        
    Returns:
        Dictionary with tool results as messages.
    """
    result = []
    last_message = state["messages"][-1]
    
    # Process each tool call from the LLM's response
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Get the tool and execute it
        tool = tools_by_name.get(tool_name)
        if tool:
            observation = tool.invoke(tool_args)
            result.append(
                ToolMessage(
                    content=str(observation),
                    tool_call_id=tool_call["id"]
                )
            )
        else:
            result.append(
                ToolMessage(
                    content=f"Error: Tool '{tool_name}' not found.",
                    tool_call_id=tool_call["id"]
                )
            )
    
    return {"messages": result}


def should_continue(state: ChefState) -> Literal["tool_node", "__end__"]:
    """Determine whether to continue with tool execution or end.
    
    Args:
        state: Current agent state.
        
    Returns:
        "tool_node" if there are tool calls to execute, "__end__" otherwise.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM made tool calls, execute them
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tool_node"
    
    # Otherwise, end the conversation turn
    return "__end__"
