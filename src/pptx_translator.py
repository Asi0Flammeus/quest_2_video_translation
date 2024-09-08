from pptx import Presentation

def translate_txt_to(text, code_language):
    # Simulated translation function (replace with actual translation logic)
    return text+code_language

# Load your presentation
prs = Presentation('../test/lnp201-en.pptx')

for slide in prs.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text_frame = shape.text_frame
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                # Translate the text
                translated_text = translate_txt_to(run.text, "es")  # Example: translate to Spanish
                # Replace original text with translated text
                run.text = translated_text

# Save the modified presentation to a new file
prs.save('../test/translated_presentation.pptx')
