from pathlib import Path
from dotenv import load_dotenv
import os
import anthropic

def setup_anthropic_client():
    # Get the parent directory of the current file
    parent_dir = Path(__file__).parent.parent

    # Load environment variables from .env file
    load_dotenv(dotenv_path=parent_dir / '.env')

    # Get the API key from environment variables
    API_KEY_ANTHROPIC = os.getenv('API_KEY_ANTHROPIC')

    # Create and return the Anthropic client
    return anthropic.Anthropic(api_key=API_KEY_ANTHROPIC)

# Create a global client instance
anthropic_client = setup_anthropic_client()
