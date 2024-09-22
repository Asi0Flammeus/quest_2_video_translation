import anthropic
import tiktoken
from config import anthropic_client

def split_text(text, max_tokens=1750):
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for token in tokens:
        current_chunk.append(token)
        current_token_count += 1
        
        if current_token_count >= max_tokens:
            # Convert tokens back to text
            chunk_text = enc.decode(current_chunk)
            # Find the last complete sentence
            last_period = chunk_text.rfind('.')
            if last_period != -1:
                chunks.append(chunk_text[:last_period+1])
                # Start the next chunk with the remainder
                current_chunk = enc.encode(chunk_text[last_period+1:])
                current_token_count = len(current_chunk)
            else:
                # If no period found, just use the whole chunk
                chunks.append(chunk_text)
                current_chunk = []
                current_token_count = 0
    
    # Add any remaining text as the last chunk
    if current_chunk:
        chunks.append(enc.decode(current_chunk))
    
    return chunks

def translate_txt_to(text, language):
    try:
        chunks = split_text(text)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            print(f"Translating in progress ... [{i+1}/{len(chunks)}]")
            #TODO: Replace this part with function for get_translation_from_claude 
            # and write another one for openai
            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=5000,
                temperature=0.2,
                system=f"Your task is to accurately translate this text into {language}. Only output the translation. If there's nothing to translate simply output the original text.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"string to translate:\n {chunk}"
                            }
                        ]
                    }
                ]
            )
            
            translated_chunk = message.content[0].text
            translated_chunks.append(translated_chunk)
        
        return " ".join(translated_chunks)
    except Exception as e:
        raise TranslationError(f"Translation failed: {str(e)}")

def save_translation(content, path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)


class TranslationError(Exception):
    pass
