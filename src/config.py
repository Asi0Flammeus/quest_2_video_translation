from pathlib import Path
from dotenv import load_dotenv
import os
import anthropic
import json

parent_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=parent_dir / '.env')

API_KEY_ANTHROPIC = os.getenv('API_KEY_ANTHROPIC')
anthropic_client = anthropic.Anthropic(api_key=API_KEY_ANTHROPIC)

API_KEY_ELEVENLABS = os.getenv("API_KEY_ELEVENLABS")
HEADERS = {
    "Accept": "application/json",
    "xi-api-key": API_KEY_ELEVENLABS,
    "Content-Type": "application/json"
}
voice_ids_json = os.linesep.join(os.getenv('VOICE_IDS').splitlines())
voice_ids = json.loads(voice_ids_json)
