"""
Constants for the Compair API.

This module contains configuration constants including LLM model settings
and API keys.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = "gpt-4o"
OPENAI_TEMPERATURE = 0.7

# Brave Search API Configuration
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"
BRAVE_SEARCH_COUNT = int(os.getenv("BRAVE_SEARCH_COUNT", "5"))  # Number of search results to fetch
BRAVE_SEARCH_SNIPPETS = int(os.getenv("BRAVE_SEARCH_SNIPPETS", "5"))  # Number of snippets to include in summary
BRAVE_SEARCH_TIMEOUT = int(os.getenv("BRAVE_SEARCH_TIMEOUT", "10"))  # API request timeout in seconds

# FastAPI Configuration
APP_TITLE = "COMPAIR API"

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://compair.com"
]

# Data Storage Configuration
HISTORY_FILE = "comparison_history.json"
SHARED_FILE = "shared_comparisons.json"

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Share Configuration
SHARE_URL_BASE = "https://compair.com/shared/"
SHARE_ID_LENGTH = 8

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./compair.db")
# For PostgreSQL, use: postgresql://user:password@localhost:5432/compair
# For SQLite (default): sqlite:///./compair.db

# Validation Configuration
MIN_ITEMS_TO_COMPARE = 2
MIN_ITEM_LENGTH = 2

