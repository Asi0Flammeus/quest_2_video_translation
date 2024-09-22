from pathlib import Path
from dotenv import load_dotenv
import os
import anthropic
import json

parent_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=parent_dir / '.env')

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
CHUNK_SIZE = 1024
VOICE_IDS = os.getenv("voice_ids")

API_KEY_ANTHROPIC = os.getenv('API_KEY_ANTHROPIC')
anthropic_client = anthropic.Anthropic(api_key=API_KEY_ANTHROPIC)
voice_ids_json = os.linesep.join(os.getenv('VOICE_IDS').splitlines())

voice_ids = json.loads(voice_ids_json)
