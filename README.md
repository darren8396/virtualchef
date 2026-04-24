# 🍳 VirtualChef - AI Recipe Finder

A conversational AI chef application that helps you discover recipes based on ingredients you have available. Built with LangGraph, Gemini 2.0 Flash, and Streamlit.

## Features

- **Ingredient-Based Recipe Search**: Tell the chef what's in your fridge
- **Web-Powered Results**: Uses Tavily to search for real recipes online
- **Dietary Preferences**: Filter by vegetarian, vegan, gluten-free, and more
- **Cooking Time Filter**: Set maximum cooking time for quick meal ideas
- **Conversational Interface**: Natural chat experience with follow-up questions

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | LangGraph v1.0+ |
| LLM | Gemini 2.0 Flash |
| Web Search | Tavily Search API |
| UI | Streamlit |

## Quick Start

### 1. Clone and Navigate

```bash
cd virtualchef
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys

Copy the example environment file and add your API keys:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Edit `.env` and add your keys:

```
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

#### Getting API Keys

**Google AI Studio (Gemini)**
1. Go to https://aistudio.google.com/
2. Click "Get API Key"
3. Create a new API key
4. Copy and save as `GOOGLE_API_KEY`

**Tavily Search**
1. Go to https://tavily.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy and save as `TAVILY_API_KEY`

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Enter Ingredients**: Type what you have available (e.g., "I have chicken, garlic, lemon, and olive oil")
2. **Set Preferences**: Use the sidebar to select dietary restrictions and max cooking time
3. **Get Recipes**: The AI chef will search for recipes and present options
4. **Ask Follow-ups**: Request more details, substitutions, or different suggestions

## Project Structure

```
virtualchef/
├── app.py                  # Streamlit entry point
├── agent/
│   ├── __init__.py         # Package exports
│   ├── state.py            # ChefState TypedDict
│   ├── tools.py            # Tavily search tool
│   ├── model.py            # Gemini model config
│   ├── nodes.py            # LLM call, tool node, routing
│   └── graph.py            # StateGraph workflow
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── PLAN.md                 # Implementation plan
├── TODO.md                 # Development checklist
└── README.md               # This file
```

## Architecture

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
```

## Future Enhancements

- [ ] Streaming responses for real-time output
- [ ] Memory persistence across sessions
- [ ] Image upload for fridge photos
- [ ] Recipe saving and favorites
- [ ] Nutritional information display

## License

MIT
