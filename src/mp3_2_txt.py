import os
import re
import time
import requests
import openai
import tiktoken
from pydub import AudioSegment
from dotenv import load_dotenv
from openai.error import RateLimitError, Timeout, APIError

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def split_text_into_chunks(text: str, MAX_TOKENS: int = 1000,
        ENCODING_NAME: str = "cl100k_base", transcript: bool = False) -> list:
    """
    Splits the input text into chunks with a maximum token count, preserving original layout.

    Args:
        text (str): The input text to be split.
        MAX_TOKENS (int): The maximum token count for each chunk (default: 1000).
        ENCODING_NAME (str): The encoding name to be used for tokenization (default: "cl100k_base").

    Returns:
        list: The list of chunks.
    """
    chunks = []
    current_chunk = ""

    if transcript:
        sentences = re.split(r'\.\s+', text)  
        for sentence in sentences:
            sentence_tokens = num_tokens_from_string(sentence, ENCODING_NAME)
            if sentence_tokens + num_tokens_from_string(current_chunk, ENCODING_NAME) <= MAX_TOKENS:
                current_chunk += sentence + ". "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
    else:
        paragraphs = text.splitlines()  
        for paragraph in paragraphs:
            paragraph_tokens = num_tokens_from_string(paragraph, ENCODING_NAME)

            if paragraph_tokens + num_tokens_from_string(current_chunk, ENCODING_NAME) <= MAX_TOKENS:
                current_chunk += paragraph + "\n"  
            else:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

class TranscriptionModel:
    """
    This class provides functionality to transcribe audio files using OpenAI's Whisper API
    """

    AUDIO_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.webm', '.mp4', '.mpga', '.mpeg')
    MAX_SUPPORTED_AUDIO_SIZE_MB = 20  

    load_dotenv()
    openai.api_key = os.getenv("API_KEY_OPENAI")

    def __init__(self, output_dir):
        self.transcript = None
        self.original_audio_file = []
        self.audio_files = []
        self.output_dir = output_dir

    def save_text(self, text: str, suffix: str):
        """
        Save a text to the output folder with a specific suffix.

        Args:
            text (str): The text to be saved.
            suffix (str): The suffix to use for the saved text file name.
        """

        audio_file_name = os.path.basename(self.original_audio_file[0])
        os.makedirs(self.output_dir, exist_ok=True)
        file_path = os.path.join(self.output_dir, os.path.splitext(audio_file_name)[0] + f"{suffix}.txt")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)


    def load_audio(self, file_path):
        """
        Loads an audio file from the specified file path.

        Args:
            file_path (str): The path to the audio file.

        Raises:
            ValueError: If the file path is not valid or does not have a valid audio file extension.
        """
        if not os.path.isfile(file_path) or not file_path.endswith(self.AUDIO_EXTENSIONS):
            raise ValueError(f"Invalid audio file: {file_path}")

        self.transcript = None
        self.original_audio_file = []
        self.audio_files = []

        self.original_audio_file.append(file_path)

        audio_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if audio_size_mb > self.MAX_SUPPORTED_AUDIO_SIZE_MB:
            chunk_size_ms = self.MAX_SUPPORTED_AUDIO_SIZE_MB * 1024 * 1024 * 8 // 1000
            audio = AudioSegment.from_file(file_path)
            duration_ms = len(audio)

            for i in range(0, duration_ms, chunk_size_ms):
                chunk = audio[i:i + chunk_size_ms]
                chunk_file_path = f"{os.path.splitext(file_path)[0]}_{i // chunk_size_ms}{os.path.splitext(file_path)[1]}"
                chunk.export(chunk_file_path, format=file_path.split('.')[-1])
                self.audio_files.append(chunk_file_path)
        else:
            self.audio_files.append(file_path)

    def transcribe_audio(self):
        """
        Transcribes the audio data using OpenAI's Whisper API.
        Returns:
            str: The transcript of the audio data in text format.
        """
        if not self.audio_files:
            raise ValueError("No audio files have been loaded.")

        file_path = self.audio_files[0]
        audio_file = open(file_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        audio_file.close()

        # Extract the transcript text
        transcript_text = transcript["text"]

        return transcript_text

    def transcribe_multiple_chunks_audio(self):
        """
        Transcribes all the audio chunks into a single transcript

        Returns:
            str: The transcript of the audio data in text format.
        """
        if not self.audio_files:
            raise ValueError("No audio files have been loaded.")

        if len(self.audio_files) > 1:
            sub_audio_file = True
        else:
            sub_audio_file = False

        file_path = self.original_audio_file[0]
        transcript_file = f"./outputs/{os.path.splitext(os.path.basename(file_path))[0]}_French_transcript.txt"

        if os.path.exists(transcript_file):
            with open(transcript_file, 'r') as f:
                transcript_text = f.read()
            self.transcript = transcript_text
            print("already there")
            while self.audio_files:
                if sub_audio_file:
                    os.remove(self.audio_files[0])
                self.audio_files.pop(0)
            return transcript_text

        transcript_texts = []

        while self.audio_files:
            transcript_text = self.transcribe_audio()
            transcript_texts.append(transcript_text)
            if sub_audio_file:
                os.remove(self.audio_files[0])
            self.audio_files.pop(0)

        self.transcript =  "".join(transcript_texts)
        self.save_text(self.transcript, "")

        return self.transcript


    def load_and_transcribe_audio(self, audio_file):
        self.load_audio(audio_file)
        transcript = self.transcribe_multiple_chunks_audio()
        print("Transcript done!")

        return transcript



# TODO: change the save process to a given path 
