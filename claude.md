# AI Chef Application - Development Plan
## Using LangGraph v1 & Gemini 2.0 Flash

> **Note**: There is no "Gemini 3.0 Flash" model. This plan uses **Gemini 2.0 Flash** (`gemini-2.0-flash-exp`) or alternatively **Gemini 2.5 Flash Lite** (`gemini-2.5-flash-lite`), which are the latest available Gemini models.

---

## 1. Overview

A conversational AI chef application that helps users discover recipes based on ingredients they have available. Users interact through a Streamlit chat interface, tell the app what's in their fridge, and receive personalized recipe suggestions fetched from the web.

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Agent Framework** | LangGraph v1.0+ |
| **LLM** | Gemini 2.0 Flash (via `langchain-google-genai`) |
| **Web Search** | Tavily Search API |
| **UI** | Streamlit |
| **State Management** | LangGraph StateGraph with TypedDict |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Chat Interface (st.chat_message / st.chat_input)   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   LANGGRAPH AGENT                           │
│                                                             │
│   ┌─────────┐    ┌──────────────┐    ┌─────────────────┐   │
│   │  START  │───▶│   llm_call   │───▶│ should_continue │   │
│   └─────────┘    └──────────────┘    └────────┬────────┘   │
│                         ▲                      │            │
│                         │              ┌───────┴───────┐    │
│                         │              ▼               ▼    │
│                  ┌──────┴──────┐  ┌─────────┐    ┌─────┐   │
│                  │  tool_node  │  │  tools  │    │ END │   │
│                  └─────────────┘  └─────────┘    └─────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
┌───────────────────┐         ┌───────────────────┐
│  Gemini 2.0 Flash │         │  Tavily Search    │
│  (LLM)            │         │  (Web Search)     │
└───────────────────┘         └───────────────────┘
```

---

## 3. Project Structure

```
ai-chef/
├── app.py                      # Streamlit entry point
├── agent/
│   ├── __init__.py
│   ├── graph.py                # LangGraph workflow definition
│   ├── state.py                # State schema (TypedDict)
│   ├── nodes.py                # Node functions
│   └── tools.py                # Tool definitions (Tavily search)
├── config.py                   # Configuration and API keys
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Implementation Guide

### Phase 1: Environment Setup

#### 4.1 Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install langgraph langchain langchain-google-genai langchain-community
pip install tavily-python streamlit python-dotenv
```

#### 4.2 Dependencies File

```txt
# requirements.txt
langgraph>=1.0.0
langchain>=1.0.0
langchain-google-genai>=2.0.0
langchain-community>=0.3.0
tavily-python>=0.5.0
streamlit>=1.40.0
python-dotenv>=1.0.0
```

#### 4.3 Environment Variables

```bash
# .env.example
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

---

### Phase 2: Define State Schema

Based on the latest LangGraph documentation, state is defined using `TypedDict` with the `Annotated` type for reducers.

```python
# agent/state.py
from typing import Annotated, List
from typing_extensions import TypedDict
from langchain.messages import AnyMessage
import operator


class ChefState(TypedDict):
    """State schema for the AI Chef agent.
    
    Attributes:
        messages: Conversation history with add reducer
        ingredients: List of ingredients from user's fridge
        dietary_preferences: Any dietary restrictions or preferences
    """
    messages: Annotated[list[AnyMessage], operator.add]
    ingredients: List[str]
    dietary_preferences: str
```

---

### Phase 3: Define Tools

Using Tavily for web search (recommended by LangChain for recipe search).

```python
# agent/tools.py
from langchain.tools import tool
from langchain_community.tools import TavilySearchResults


def get_search_tool():
    """Create and return the Tavily search tool for recipe searches."""
    return TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_raw_content=True,
        name="search_recipes",
        description="Search the web for recipes based on ingredients. Use this to find recipes that match the user's available ingredients."
    )


@tool
def search_recipes(query: str) -> str:
    """Search for recipes on the web.
    
    Args:
        query: Search query combining ingredients and any preferences
        
    Returns:
        String containing recipe search results
    """
    search = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_raw_content=True
    )
    results = search.invoke(query)
    return str(results)
```

---

### Phase 4: Configure the Model

Using `init_chat_model` (the recommended approach in LangChain v1) or direct instantiation.

```python
# agent/model.py
import os
from dotenv import load_dotenv

load_dotenv()

# Option 1: Using init_chat_model (recommended)
from langchain.chat_models import init_chat_model

def get_model():
    """Initialize and return the Gemini model."""
    return init_chat_model(
        "google_genai:gemini-2.0-flash-exp",
        temperature=0.7
    )


# Option 2: Direct instantiation
from langchain_google_genai import ChatGoogleGenerativeAI

def get_model_direct():
    """Initialize Gemini model directly."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
```

---

### Phase 5: Build the LangGraph Agent

Following the official LangGraph v1 quickstart pattern:

```python
# agent/graph.py
from typing import Literal
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from .state import ChefState
from .tools import search_recipes


# Initialize model with tools
model = init_chat_model("google_genai:gemini-2.0-flash-exp", temperature=0.7)
tools = [search_recipes]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


# System prompt for the chef agent
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

If the user has dietary restrictions, always respect them when searching for recipes."""


def llm_call(state: ChefState):
    """Call the LLM to process user input and decide on actions."""
    messages = [
        SystemMessage(content=CHEF_SYSTEM_PROMPT)
    ] + state["messages"]
    
    response = model_with_tools.invoke(messages)
    
    return {"messages": [response]}


def tool_node(state: ChefState):
    """Execute tool calls made by the LLM."""
    result = []
    last_message = state["messages"][-1]
    
    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(
            ToolMessage(
                content=str(observation), 
                tool_call_id=tool_call["id"]
            )
        )
    
    return {"messages": result}


def should_continue(state: ChefState) -> Literal["tool_node", "__end__"]:
    """Determine whether to continue with tool execution or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM made tool calls, execute them
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tool_node"
    
    # Otherwise, end the conversation turn
    return END


def create_chef_agent():
    """Build and compile the chef agent graph."""
    # Create the state graph
    workflow = StateGraph(ChefState)
    
    # Add nodes
    workflow.add_node("llm_call", llm_call)
    workflow.add_node("tool_node", tool_node)
    
    # Add edges
    workflow.add_edge(START, "llm_call")
    workflow.add_conditional_edges(
        "llm_call",
        should_continue,
        ["tool_node", END]
    )
    workflow.add_edge("tool_node", "llm_call")
    
    # Compile and return
    return workflow.compile()


# Create the agent instance
chef_agent = create_chef_agent()
```

---

### Phase 6: Build the Streamlit UI

```python
# app.py
import streamlit as st
from langchain.messages import HumanMessage, AIMessage
from agent.graph import chef_agent

# Page configuration
st.set_page_config(
    page_title="AI Chef - Recipe Finder",
    page_icon="🍳",
    layout="wide"
)

# Title and description
st.title("🍳 AI Chef - Recipe Finder")
st.markdown("Tell me what's in your fridge, and I'll find delicious recipes for you!")

# Sidebar for preferences
with st.sidebar:
    st.header("🥗 Dietary Preferences")
    dietary_prefs = st.multiselect(
        "Select any dietary restrictions:",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "Low-Carb"],
        default=[]
    )
    
    st.header("⏱️ Cooking Time")
    max_time = st.slider("Maximum cooking time (minutes):", 15, 120, 45)
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant", avatar="🍳"):
            st.markdown(message.content)

# Chat input
if prompt := st.chat_input("What ingredients do you have? (e.g., 'I have chicken, rice, and broccoli')"):
    # Add user message to state
    user_message = HumanMessage(content=prompt)
    st.session_state.messages.append(user_message)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Build context with preferences
    preferences_context = ""
    if dietary_prefs:
        preferences_context = f" (Dietary preferences: {', '.join(dietary_prefs)})"
    if max_time:
        preferences_context += f" (Max cooking time: {max_time} minutes)"
    
    # Prepare state for the agent
    agent_state = {
        "messages": st.session_state.messages,
        "ingredients": [],
        "dietary_preferences": ", ".join(dietary_prefs) if dietary_prefs else ""
    }
    
    # Get response from agent
    with st.chat_message("assistant", avatar="🍳"):
        with st.spinner("🔍 Searching for recipes..."):
            try:
                # Invoke the agent
                result = chef_agent.invoke(agent_state)
                
                # Get the last AI message
                ai_messages = [
                    msg for msg in result["messages"] 
                    if isinstance(msg, AIMessage) and msg.content
                ]
                
                if ai_messages:
                    response_content = ai_messages[-1].content
                    st.markdown(response_content)
                    st.session_state.messages.append(AIMessage(content=response_content))
                else:
                    st.error("No response generated. Please try again.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your API keys and try again.")

# Footer
st.markdown("---")
st.markdown("*Powered by LangGraph & Gemini 2.0 Flash* 🤖")
```

---

## 5. Running the Application

```bash
# Set environment variables
export GOOGLE_API_KEY="your_google_api_key"
export TAVILY_API_KEY="your_tavily_api_key"

# Run the Streamlit app
streamlit run app.py
```

---

## 6. Key Patterns from LangGraph v1 Documentation

### 6.1 State Definition Pattern
```python
from typing import Annotated
from typing_extensions import TypedDict
import operator

class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]  # Uses reducer
    custom_field: str  # No reducer, overwrites
```

### 6.2 Graph Construction Pattern
```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(State)
workflow.add_node("node_name", node_function)
workflow.add_edge(START, "node_name")
workflow.add_conditional_edges("node_name", condition_func, ["next_node", END])
workflow.add_edge("next_node", END)
agent = workflow.compile()
```

### 6.3 Tool Binding Pattern
```python
from langchain.tools import tool

@tool
def my_tool(arg: str) -> str:
    """Tool description."""
    return result

model_with_tools = model.bind_tools([my_tool])
```

### 6.4 Conditional Edge Pattern
```python
from typing import Literal

def should_continue(state: State) -> Literal["tool_node", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END  # or "__end__"
```

---

## 7. Testing

### 7.1 Test the Agent Independently

```python
# test_agent.py
from langchain.messages import HumanMessage
from agent.graph import chef_agent

def test_chef_agent():
    state = {
        "messages": [
            HumanMessage(content="I have chicken, garlic, lemon, and olive oil")
        ],
        "ingredients": [],
        "dietary_preferences": ""
    }
    
    result = chef_agent.invoke(state)
    
    print("Agent Response:")
    for msg in result["messages"]:
        print(f"[{type(msg).__name__}]: {msg.content[:200]}...")

if __name__ == "__main__":
    test_chef_agent()
```

---

## 8. Enhancements (Future Iterations)

| Feature | Description |
|---------|-------------|
| **Memory/Checkpointing** | Add `InMemorySaver` or persistent checkpointer for conversation history |
| **Streaming** | Use `agent.stream()` for real-time token streaming |
| **Multiple Search Sources** | Add additional recipe APIs (Spoonacular, Edamam) |
| **Image Support** | Allow users to upload fridge photos (Gemini vision) |
| **Recipe Saving** | Save favorite recipes to a database |
| **Nutrition Info** | Add nutritional analysis for recipes |

---

## 9. API Keys Setup

### Google AI Studio (Gemini)
1. Go to https://aistudio.google.com/
2. Click "Get API Key"
3. Create a new API key
4. Copy and save as `GOOGLE_API_KEY`

### Tavily Search
1. Go to https://tavily.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy and save as `TAVILY_API_KEY`

---

## 10. Summary

This plan follows the **latest LangGraph v1 patterns** as documented:

✅ `StateGraph` with `TypedDict` state schema  
✅ `START` and `END` constants for graph edges  
✅ `operator.add` reducer for message lists  
✅ `init_chat_model()` for model initialization  
✅ `@tool` decorator for tool definitions  
✅ `bind_tools()` for attaching tools to models  
✅ Conditional edges with `Literal` type hints  
✅ Proper tool node pattern with `ToolMessage`  

The architecture provides a clean separation between the LangGraph agent logic and the Streamlit UI, making it easy to extend and maintain.