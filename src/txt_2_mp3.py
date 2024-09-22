import os
from pathlib import Path
import requests

from config import HEADERS

def text_to_speech(text_filepath, voice_id):
    text_filepath = Path(text_filepath)
    output_path = text_filepath.with_suffix(".mp3")
    if output_path.exists():
        print(f"Skipping {output_path}, file already exists.")
        return
    text_to_speak = text_filepath.read_text()
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    data = {
        "text": text_to_speak,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    response = requests.post(tts_url, headers=HEADERS, json=data, stream=False)
    if response.ok:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Audio stream saved successfully to {output_path}")
    else:
        raise Exception(f"API Request Failed: {response.text}")
