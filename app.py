"""
VirtualChef - Streamlit Application

A conversational AI chef that helps users find recipes based on
their available ingredients.
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agent import chef_agent


def _extract_text(content) -> str:
    """Extract a plain string from content that may be a string or a list
    of content blocks (e.g. [{"type": "text", "text": "..."}]) as returned
    by some Gemini model versions."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return str(content)
from config import (
    PAGE_TITLE,
    PAGE_ICON,
    DIETARY_OPTIONS,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    DEFAULT_COOKING_TIME,
    validate_config,
    sanitize_input,
    logger
)


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)

# Title and description
st.title(f"{PAGE_ICON} VirtualChef - AI Recipe Finder")
st.markdown(
    "Tell me what's in your fridge, and I'll find delicious recipes for you! "
    "Just type your ingredients below and I'll search for the perfect recipes."
)

# Sidebar for preferences
with st.sidebar:
    st.header("🥗 Dietary Preferences")
    dietary_prefs = st.multiselect(
        "Select any dietary restrictions:",
        DIETARY_OPTIONS,
        default=[],
        help="Your recipes will be filtered to match these preferences"
    )
    
    st.header("⏱️ Cooking Time")
    max_time = st.slider(
        "Maximum cooking time (minutes):",
        MIN_COOKING_TIME,
        MAX_COOKING_TIME,
        DEFAULT_COOKING_TIME,
        help="Filter recipes by preparation and cooking time"
    )
    
    st.divider()
    
    st.header("💡 Tips")
    st.markdown("""
    - List your main ingredients
    - Mention any preferences
    - Ask for specific cuisines
    - Request quick meals
    """)
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant", avatar=PAGE_ICON):
            st.markdown(message.content)

# Chat input
if prompt := st.chat_input("What ingredients do you have? (e.g., 'I have chicken, rice, and broccoli')"):
    # Validate configuration before processing
    try:
        validate_config()
    except ValueError as e:
        st.error(str(e))
        st.stop()
    
    # Sanitize user input to prevent prompt injection
    sanitized_prompt, is_valid = sanitize_input(prompt)
    if not is_valid:
        st.error("Your input could not be processed. Please try rephrasing your request.")
        st.stop()
    
    # Add user message to state
    user_message = HumanMessage(content=sanitized_prompt)
    st.session_state.messages.append(user_message)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(sanitized_prompt)
    
    # Prepare state for the agent
    agent_state = {
        "messages": st.session_state.messages,
        "ingredients": [],
        "dietary_preferences": ", ".join(dietary_prefs) if dietary_prefs else "",
        "max_cooking_time": max_time
    }
    
    # Get response from agent
    with st.chat_message("assistant", avatar=PAGE_ICON):
        with st.spinner("🔍 Searching for recipes..."):
            try:
                # Invoke the agent
                result = chef_agent.invoke(agent_state)
                
                # Get the last AI message from results
                ai_messages = [
                    msg for msg in result["messages"]
                    if isinstance(msg, AIMessage) and msg.content
                ]
                
                if ai_messages:
                    response_content = _extract_text(ai_messages[-1].content)
                    st.markdown(response_content)
                    st.session_state.messages.append(
                        AIMessage(content=response_content)
                    )
                else:
                    st.error("No response generated. Please try again.")
                    
            except Exception as e:
                # Log the full error for debugging (server-side only)
                logger.error(f"Error processing request: {str(e)}", exc_info=True)
                # Show generic message to user (don't expose internal details)
                st.error("An error occurred while processing your request. Please try again.")
                st.info(
                    "If this problem persists, please check that your API keys are properly configured."
                )

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.caption("Powered by LangGraph & Gemini 2.5 Flash 🤖")
