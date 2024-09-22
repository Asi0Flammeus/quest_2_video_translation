from config import VOICE_IDS
from mp3_2_txt import TranscriptionModel 
from txt_2_mp3 import text_to_speech
from txt_translation import save_translation, translate_txt_to

path = "../test/scu101/fr/v001/2.1/slides/2.1.01_rogzy.txt"
text_to_speech(path, VOICE_IDS["rogzy"])

