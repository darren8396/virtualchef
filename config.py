"""
VirtualChef Configuration Module

Centralizes all configuration and environment variable loading.
"""

import os
import re
import logging
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _get_secret(key: str) -> str | None:
    """Read a secret from st.secrets (Streamlit Cloud) or fall back to env var.

    Streamlit Community Cloud stores secrets via the dashboard and exposes them
    through st.secrets.  They are NOT always injected as OS env vars before
    module-level code runs, so we check st.secrets explicitly first.
    """
    # Try Streamlit secrets first (works on Streamlit Community Cloud)
    try:
        import streamlit as st
        value = st.secrets.get(key)
        if value:
            # Mirror into os.environ so third-party libraries can pick it up
            os.environ[key] = value
            return value
    except Exception:
        pass
    # Fall back to environment variable (local .env or CI/CD injection)
    return os.getenv(key)


# API Keys
GOOGLE_API_KEY = _get_secret("GOOGLE_API_KEY")
TAVILY_API_KEY = _get_secret("TAVILY_API_KEY")

# Model Configuration
MODEL_NAME = "gemini-2.5-flash"
MODEL_TEMPERATURE = 0.7

# Search Configuration
SEARCH_MAX_RESULTS = 5
SEARCH_DEPTH = "advanced"

# Streamlit Configuration
PAGE_TITLE = "AI Chef - Recipe Finder"
PAGE_ICON = "🍳"

# Dietary Options
DIETARY_OPTIONS = [
    "Vegetarian",
    "Vegan", 
    "Gluten-Free",
    "Dairy-Free",
    "Keto",
    "Low-Carb",
    "Nut-Free",
    "Halal",
    "Kosher"
]

# Cooking Time Limits (minutes)
MIN_COOKING_TIME = 15
MAX_COOKING_TIME = 120
DEFAULT_COOKING_TIME = 45

# Message History Limit (to control token usage)
MAX_MESSAGE_HISTORY = 20

# Input Sanitization Settings
MAX_INPUT_LENGTH = 2000
FORBIDDEN_PATTERNS = [
    r'(?i)ignore\s+(all\s+)?(previous|above|prior)\s+instructions',
    r'(?i)disregard\s+(all\s+)?(previous|above|prior)',
    r'(?i)you\s+are\s+now\s+in\s+',
    r'(?i)system\s*:\s*',
    r'(?i)\[\s*system\s*\]',
]


def sanitize_input(user_input: str) -> tuple[str, bool]:
    """Sanitize user input to prevent prompt injection.
    
    Args:
        user_input: Raw user input string.
        
    Returns:
        Tuple of (sanitized_input, is_valid).
        If is_valid is False, the input should be rejected.
    """
    # Check length
    if len(user_input) > MAX_INPUT_LENGTH:
        logger.warning(f"Input rejected: exceeded max length ({len(user_input)} > {MAX_INPUT_LENGTH})")
        return "", False
    
    # Check for forbidden patterns (potential prompt injection)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, user_input):
            logger.warning(f"Input rejected: matched forbidden pattern")
            return "", False
    
    # Basic cleanup - strip excessive whitespace
    sanitized = ' '.join(user_input.split())
    
    return sanitized, True


def validate_config():
    """Validate that required configuration is present."""
    missing = []
    
    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY")
    
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please copy .env.example to .env and fill in your API keys."
        )
    
    return True
