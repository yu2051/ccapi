# src/config.py
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Define a default CLI_VERSION to avoid import errors
CLI_VERSION = "1.0.0"

# Load multiple Gemini configs from a single environment variable
GEMINI_CONFIGS_JSON = os.getenv("GEMINI_CONFIGS")
GEMINI_CONFIGS = json.loads(GEMINI_CONFIGS_JSON) if GEMINI_CONFIGS_JSON else []

# Create a dictionary for easy lookup by id
GEMINI_CONFIGS_MAP = {config['id']: config for config in GEMINI_CONFIGS}

# OpenAI API key (remains unchanged)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_gemini_config_by_id(account_id: str):
    """
    Retrieves a specific Gemini configuration by its ID.
    """
    return GEMINI_CONFIGS_MAP.get(account_id)
