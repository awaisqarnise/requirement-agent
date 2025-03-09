import os
from dotenv import load_dotenv, find_dotenv

def load_environment():
    """Load API keys from .env file and return OpenAI API Key."""
    _ = load_dotenv(find_dotenv())  # Read local .env file
    return os.getenv('OPENAI_API_KEY')  # Use os.getenv to prevent crashes
