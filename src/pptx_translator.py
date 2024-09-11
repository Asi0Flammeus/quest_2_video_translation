from pptx import Presentation
from dotenv import load_dotenv
import os
import anthropic
from pathlib import Path

parent_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=parent_dir / '.env')
API_KEY_ANTHROPIC = os.getenv('API_KEY_ANTHROPIC')
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
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
def translate_txt_to(text, language):
    try:
        # Simulated translation function (replace with actual translation logic)
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            temperature=0.2,
            system=f"You are a highly skilled translator with expertise in many languages. Your task is to accurately translate this text into {language} while preserving the meaning, tone, and nuance of the original text. Please maintain proper grammar, spelling, and punctuation in the translated version.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ]
        )
        
        # Extract only the text field from the response
        translated_text = message.content[0].text
        return translated_text
    except Exception as e:
        # Raise a custom exception with details
        raise TranslationError(f"Translation failed: {str(e)}")

# Custom exception class
class TranslationError(Exception):
    pass

print(translate_txt_to("Hello World, I'm asi0 doing some code and stuff.", language_codes["ja"]))

# Load your presentation
prs = Presentation('../test/lnp201-en.pptx')

# for slide in prs.slides:
#     for shape in slide.shapes:
#         if not shape.has_text_frame:
#             continue
#         text_frame = shape.text_frame
#         for paragraph in text_frame.paragraphs:
#             for run in paragraph.runs:
#                 # Translate the tex
#                 translated_text = translate_txt_to(run.text, "es")  # Example: translate to Spanish
#                 # Replace original text with translated text
#                 run.text = translated_text
#
# # Save the modified presentation to a new file
# prs.save('../test/translated_presentation.pptx')
# TODO: write the translation function (simple prompt with dict codelanguage language)
# TODO: loop translation except for text in the bottom banner and find EN and replace by code language
