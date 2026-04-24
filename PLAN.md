# VirtualChef - Implementation Plan

## Overview

A conversational AI chef application using LangGraph v1, Gemini 2.0 Flash, and Tavily Search with a Streamlit UI. Users describe their available ingredients and receive personalized recipe suggestions fetched from the web.

## Architecture

```
Streamlit UI → LangGraph Agent → Gemini 2.0 Flash + Tavily Search
```

## Project Structure

```
virtualchef/
├── app.py                  # Streamlit entry point
├── agent/
│   ├── __init__.py
│   ├── state.py            # ChefState TypedDict
│   ├── tools.py            # Tavily search tool
│   ├── model.py            # Gemini model config
│   ├── nodes.py            # llm_call, tool_node, should_continue
│   └── graph.py            # StateGraph workflow
├── config.py               # Centralized configuration
├── requirements.txt
├── .env.example
└── README.md
```

## Implementation Phases

### Phase 1: Project Scaffolding
- Create folder structure and empty files
- Set up `.env.example` with API key placeholders
- Verify `requirements.txt` dependencies

### Phase 2: State Schema
- Define `ChefState` TypedDict in `agent/state.py`
- Include: `messages` (with `operator.add` reducer), `ingredients`, `dietary_preferences`

### Phase 3: Model & Tools
- Implement `get_model()` in `agent/model.py` using `ChatGoogleGenerativeAI`
- Define `search_recipes` tool in `agent/tools.py` using `TavilySearchResults`

### Phase 4: LangGraph Workflow
- Implement node functions in `agent/nodes.py`:
  - `llm_call`: Invoke model with system prompt
  - `tool_node`: Execute tool calls
  - `should_continue`: Route to tools or end
- Build `StateGraph` in `agent/graph.py` with proper edges

### Phase 5: Streamlit UI
- Create chat interface with `st.chat_message` / `st.chat_input`
- Add sidebar for dietary preferences and cooking time
- Manage session state for conversation history
- Invoke agent and display responses

### Phase 6: Configuration & Documentation
- Centralize settings in `config.py`
- Update README with setup and run instructions

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | LangGraph v1.0+ |
| LLM | Gemini 2.0 Flash (`gemini-2.0-flash-exp`) |
| Web Search | Tavily Search API |
| UI | Streamlit |
| State Management | LangGraph StateGraph with TypedDict |

## Future Enhancements
- Streaming responses with `agent.stream()`
- Memory/checkpointing with `InMemorySaver`
- Image upload for fridge photos (Gemini vision)
- Recipe saving and nutrition info
