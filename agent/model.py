"""
Model Configuration for the VirtualChef Agent

Initializes and configures the Gemini 2.0 Flash model.
"""

from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI

from config import MODEL_NAME, MODEL_TEMPERATURE, GOOGLE_API_KEY


@lru_cache(maxsize=1)
def get_model():
    """Initialize and return the Gemini 2.0 Flash model.
    
    Uses lru_cache to ensure only one model instance is created.
    
    Returns:
        ChatGoogleGenerativeAI: Configured Gemini model instance.
    """
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
        google_api_key=GOOGLE_API_KEY
    )
