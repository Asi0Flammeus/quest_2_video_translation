import os
from dotenv import load_dotenv

# Config parameters 

load_dotenv()
ELVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
CHUNK_SIZE = 1024

# Voice Character
voice_ids = {
                            "Rogzy": "RmicS1jU3ei6Vxlpkqj4",
                            "David St-onge": "0PfKe742JfrBvOr7Gyx9",
                            "Fanis": "HIRH46f2SFLDptj86kJG",
                            "Loic": "hOYgbRZsrkPHWJ2kdEIu",
                            "Mogenet": "ld8UrJoCOHSibD1DlYXB",
                            "Pantamis": "naFOP0Eb03OaLMVhdCxd",
                            "Renaud": "UVJB9VPhLrNHNsH4ZatL",
                            "es-question": "5K2SjAdgoClKG1acJ17G",
                            "en-question": "ER8xHNz0kNywE1Pc5ogG"
                        }


