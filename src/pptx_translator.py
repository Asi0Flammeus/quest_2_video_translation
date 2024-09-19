from pptx import Presentation
from dotenv import load_dotenv
import os
import anthropic
from pathlib import Path
from functools import lru_cache
from tqdm import tqdm

translation_cache = {}

parent_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=parent_dir / '.env')
API_KEY_ANTHROPIC = os.getenv('API_KEY_ANTHROPIC')
client = anthropic.Anthropic(
    api_key=API_KEY_ANTHROPIC,
)
language_codes = {
    "cs": "Czech",
    "de": "German",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fi": "Finnish",
    "fr": "French",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "pt": "Portuguese",
    "ru": "Russian",
    "vi": "Vietnamese",
    "zh-Hans": "Simplified Chinese"
}

def is_exception_text(text, language_code):
    exceptions = [
        "Fanis Michalakis - ",
        "5720 CD57 7E78 94C9 8DBD 580E 8F12 D0C6 3B1A 606E"
    ]
    
    for exception in exceptions:
        if exception in text:
            if exception == "Fanis Michalakis - ":
                return text.replace("EN", language_code.upper())
            return text
    
    return None
def translate_txt_to(text, language):
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            temperature=0.2,
            system=f"Your task is to accurately translate this text into {language}. Only output the translation. If there's nothing to translate simply output the original text.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"string to translate:\n {text}"
                        }
                    ]
                }
            ]
        )
        
        translated_text = message.content[0].text
        return translated_text

    except Exception as e:
        raise TranslationError(f"Translation failed: {str(e)}")

class TranslationError(Exception):
    pass

@lru_cache(maxsize=1000)
def get_translation(text, target_language):
    """
    Check if the translation exists in cache, if not, translate and cache the result.
    """
    cache_key = (text, target_language)
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    else:
        translated_text = translate_txt_to(text, target_language)
        translation_cache[cache_key] = translated_text
        return translated_text

def count_total_runs(prs):
    total = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    total += len(paragraph.runs)
    return total

prs = Presentation('../test/22.pptx')
code_language = "zh-Hans"
total_runs = count_total_runs(prs)
progress_bar = tqdm(total=total_runs, unit='run', desc='Translating')

for slide in prs.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text_frame = shape.text_frame
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                exception_result = is_exception_text(run.text, code_language)
                if exception_result:
                    run.text = exception_result
                else:
                    translated_text = get_translation(run.text, language_codes[code_language])
                    run.text = translated_text
                
                progress_bar.update(1)
                

progress_bar.close()
prs.save(f"../test/btc204_{code_language}.pptx")
