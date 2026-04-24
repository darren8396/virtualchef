"""
LangGraph Workflow Definition for the VirtualChef Agent

Builds and compiles the StateGraph that defines the agent's
decision-making flow.
"""

from langgraph.graph import StateGraph, START, END

from .state import ChefState
from .nodes import llm_call, tool_node, should_continue


def create_chef_agent():
    """Build and compile the chef agent graph.
    
    The graph follows this flow:
    1. START -> llm_call: Process user input
    2. llm_call -> should_continue: Check for tool calls
    3. If tools needed: llm_call -> tool_node -> llm_call (loop)
    4. If no tools: llm_call -> END
    
    Returns:
        CompiledGraph: The compiled LangGraph agent ready for invocation.
    """
    # Create the state graph with our state schema
    workflow = StateGraph(ChefState)
    
    # Add nodes to the graph
    workflow.add_node("llm_call", llm_call)
    workflow.add_node("tool_node", tool_node)
    
    # Add edges
    # Entry point: START -> llm_call
    workflow.add_edge(START, "llm_call")
    
    # Conditional edge from llm_call based on tool calls
    workflow.add_conditional_edges(
        "llm_call",
        should_continue,
        {
            "tool_node": "tool_node",
            "__end__": END
        }
    )
    
    # After tool execution, go back to llm_call for processing
    workflow.add_edge("tool_node", "llm_call")
    
    # Compile and return the graph
    return workflow.compile()


# Create the agent instance for export
chef_agent = create_chef_agent()
