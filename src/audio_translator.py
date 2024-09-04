import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    print("API key is not loaded correctly.")
    exit()

# Voice Character
voice_ids = {
    "Rogzy": "RmicS1jU3ei6Vxlpkqj4",
    "Giacomo": "gFpPxLJAJCez7afCJ8Pd",
    "David St-onge": "0PfKe742JfrBvOr7Gyx9",
    "Fanis": "HIRH46f2SFLDptj86kJG",
    "Loic": "hOYgbRZsrkPHWJ2kdEIu",
    "Mogenet": "ld8UrJoCOHSibD1DlYXB",
    "Pantamis": "naFOP0Eb03OaLMVhdCxd",
    "Renaud": "UVJB9VPhLrNHNsH4ZatL",
    "es-question": "5K2SjAdgoClKG1acJ17G",
    "en-question": "ER8xHNz0kNywE1Pc5ogG"
        }

# List voices for user selection
print("Available Voices:")
for i, voice in enumerate(voice_ids.keys()):
    print(f"{i+1}. {voice}")

voice_index = int(input("Enter the number to select a voice: ")) - 1
voice_list = list(voice_ids.keys())
VOICE_ID = voice_ids[voice_list[voice_index]]

# List project folders
project_path = Path('./projects/')
project_folders = [f.name for f in project_path.iterdir() if f.is_dir()]

print("\nAvailable Project Folders:")
for i, folder in enumerate(project_folders):
    print(f"{i+1}. {folder}")

folder_index = int(input("Enter the number to select a project folder: ")) - 1
selected_folder = project_folders[folder_index]

# Headers configuration
HEADERS = {
    "Accept": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}

# Calculate API cost based on the total number of characters in text files
def calculate_api_cost(folder_name):
    folder_path = project_path / folder_name
    text_files = [text_file for text_file in folder_path.rglob("*.txt")]
    total_characters = 0
    for text_file in text_files:
        output_path = text_file.with_suffix(".mp3")
        if not output_path.exists():
            total_characters += len(text_file.read_text())
    cost = total_characters / 1000 * 0.18
    print(f"Estimated cost for API usage: {cost:.2f}€")
    return cost


# Define function for text-to-speech processing
def text_to_speech(text_file):
    output_path = text_file.with_suffix(".mp3")
    if output_path.exists():
        print(f"Skipping {output_path}, file already exists.")
        return
    text_to_speak = text_file.read_text()
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
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

# Function to process a single selected folder
def process_selected_folder(folder_name):
    cost = calculate_api_cost(folder_name)
    proceed = input("Do you want to proceed with the text-to-speech conversion? (yes/no): ")
    if proceed.lower() == 'yes':
        folder_path = project_path / folder_name
        file_patterns = ["*_transcript_English.txt", "*_transcript_Spanish.txt"]
        text_files = [text_file for pattern in file_patterns for text_file in folder_path.rglob(pattern)]
        max_workers = min(15, len(text_files))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(text_to_speech, text_file): text_file for text_file in text_files}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(e)

# Call function to process the selected folder
process_selected_folder(selected_folder)

