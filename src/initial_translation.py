import sys
import os
import re
import yaml
import subprocess
from tqdm import tqdm

from image_audio_2_video import create_video
from txt_2_mp3 import text_to_speech
from config import voice_ids
from supported_languages import *
from pptx_translator import translate_pptx
from mp3_2_txt import TranscriptionModel
from txt_translation import translate_txt_to 

# Root directory
ROOT_DIR = "../../../Documents/"  # Replace this with your actual root directory path

numbered_languages = list(enumerate(language_codes.items(), 1))

def print_separator(char="-", length=40):
    print(char * length)

def print_languages():
    print("\nAvailable languages:")
    print_separator()
    for number, (code, name) in numbered_languages:
        print(f"{number:2}. {name:20} ({code})")
    print_separator()

def get_language_choice(prompt, multiple=False, default=None):
    while True:
        if default:
            prompt = f"{prompt} (default: {default}): "
        try:
            user_input = input(prompt).strip()
            if default and user_input == "":
                return default if not multiple else [default]
            
            if multiple:
                choices = user_input.split(',')
                selected = [numbered_languages[int(choice.strip()) - 1][1][0] for choice in choices]
                if len(selected) == len(set(selected)):  # Check for duplicates
                    return selected
                print("Duplicate selections are not allowed. Please try again.")
            else:
                choice = int(user_input)
                if 1 <= choice <= len(numbered_languages):
                    return numbered_languages[choice - 1][1][0]  # Return the language code
            print("Invalid number(s). Please try again.")
        except (ValueError, IndexError):
            print("Please enter valid number(s).")

def select_directory():
    subdirs = [d for d in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, d))]
    
    if not subdirs:
        print("No subdirectories found in the root directory.")
        sys.exit(1)
    
    print("\nAvailable courses (subdirectories):")
    print_separator()
    for i, subdir in enumerate(subdirs, 1):
        print(f"{i:2}. {subdir}")
    print_separator()
    
    while True:
        try:
            choice = int(input("Enter the number for the course (subdirectory): "))
            if 1 <= choice <= len(subdirs):
                return os.path.join(ROOT_DIR, subdirs[choice - 1])
            print("Invalid number. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_latest_version(directory):
    version_dirs = [d for d in os.listdir(directory) if re.match(r'v\d{3}', d)]
    if not version_dirs:
        return None
    return max(version_dirs)

def select_source_version(course_dir, source_lang):
    lang_dir = os.path.join(course_dir, source_lang)
    if not os.path.exists(lang_dir):
        print(f"No directory found for language: {source_lang}")
        return None

    latest_version = get_latest_version(lang_dir)
    if not latest_version:
        print(f"No version folders found for language: {source_lang}")
        return None

    print(f"\nLatest version found: {latest_version}")
    use_latest = input("Do you want to use this version? (y/n): ").lower().strip()

    if use_latest == 'y':
        return latest_version

    print("\nAvailable versions:")
    versions = sorted([d for d in os.listdir(lang_dir) if re.match(r'v\d{3}', d)])
    for i, version in enumerate(versions, 1):
        print(f"{i:2}. {version}")

    while True:
        try:
            choice = int(input("Enter the number for the version you want to use: "))
            if 1 <= choice <= len(versions):
                return versions[choice - 1]
            print("Invalid number. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_original_language(course_dir):
    course_yaml = os.path.join(course_dir, 'course.yml')
    if os.path.exists(course_yaml):
        with open(course_yaml, 'r') as file:
            try:
                course_data = yaml.safe_load(file)
                return course_data.get('original_language')
            except yaml.YAMLError:
                print("Error reading course.yml file.")
    return None

def select_languages(course_dir):
    print_languages()
    
    original_lang = get_original_language(course_dir)
    if original_lang:
        print(f"\nOriginal language found in course.yml: {language_codes.get(original_lang, original_lang)} ({original_lang})")
        use_original = input("Do you want to use this as the source language? (y/n): ").lower().strip()
        if use_original == 'y':
            source_lang = original_lang
        else:
            source_lang = get_language_choice("\nEnter the number for the source language")
    else:
        source_lang = get_language_choice("\nEnter the number for the source language")
    
    while True:
        target_langs = get_language_choice("Enter the numbers for the target languages (comma-separated): ", multiple=True)
        if source_lang not in target_langs:
            return source_lang, target_langs
        print("Source language cannot be in target languages. Please try again.")
def prepare_target_folders(course_dir, source_lang, target_langs, source_version):
    def copy_folder_structure(src, dst):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                if "-DNT" not in item:  # Skip folders with "-DNT" in their name
                    if not os.path.exists(d):
                        os.makedirs(d)
                    copy_folder_structure(s, d)

    source_v001_path = os.path.join(course_dir, source_lang, 'v001')
    if not os.path.exists(source_v001_path):
        print(f"Error: v001 folder not found for source language {source_lang}")
        return 

    target_version_paths = []
    for target_lang in target_langs:
        target_lang_path = os.path.join(course_dir, target_lang)
        
        if not os.path.exists(target_lang_path):
            # Create new language folder and copy v001 structure
            os.makedirs(target_lang_path)
            new_version_path = os.path.join(target_lang_path, 'v001')
            os.makedirs(new_version_path)
            copy_folder_structure(source_v001_path, new_version_path)
            print(f"Created new folder structure for {target_lang}")
        else:
            # Ask user if they want to use the last version or create a new one
            latest_version = get_latest_version(target_lang_path)
            if latest_version:
                use_latest = input(f"Latest version for {target_lang} is {latest_version}. Use this version? (y/n): ").lower().strip()
                if use_latest == 'y':
                    new_version_path = os.path.join(target_lang_path, latest_version)
                    print(f"Using existing version {latest_version} for {target_lang}")
                else:
                    new_version_num = int(latest_version[1:]) + 1
                    new_version = f'v{new_version_num:03d}'
                    new_version_path = os.path.join(target_lang_path, new_version)
                    os.makedirs(new_version_path)
                    copy_folder_structure(os.path.join(course_dir, source_lang, source_version), new_version_path)
                    print(f"Created new version {new_version} for {target_lang}")
            else:
                new_version_path = os.path.join(target_lang_path, 'v001')
                os.makedirs(new_version_path)
                copy_folder_structure(source_v001_path, new_version_path)
                print(f"Created new folder structure for {target_lang}")

        target_version_paths.append(new_version_path)
    return target_version_paths


def convert_pptx_to_png(pptx_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bash_script_path = os.path.join(current_dir, 'pptx_2_png.sh')
    if not os.path.exists(bash_script_path):
        print(f"Error: Bash script not found at {bash_script_path}")
        return

    command = ['/bin/bash', bash_script_path, pptx_path]
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")

def translate_pptx_in_subfolders(source_version_path, source, target_version_path, target):
    subfolders = [f for f in os.listdir(source_version_path) if os.path.isdir(os.path.join(source_version_path, f)) and "-DNT" not in f]
    subfolders = sorted(subfolders)
    for subfolder in tqdm(subfolders, desc=f"Translating PowerPoint", unit="folder"):
        subfolder_path = os.path.join(source_version_path, subfolder)
        pptx_file = f"{subfolder}.pptx"
        source_pptx_path = os.path.join(subfolder_path, pptx_file)

        if os.path.exists(source_pptx_path):
            target_subfolder_path = os.path.join(target_version_path, subfolder)
            os.makedirs(target_subfolder_path, exist_ok=True)
            target_pptx_path = os.path.join(target_subfolder_path, pptx_file)

            if not os.path.exists(target_pptx_path):
                target_version = os.path.basename(os.path.normpath(target_version_path))
                translate_pptx(source_pptx_path, target_pptx_path, source, target, target_version, use_exception=True)
                convert_pptx_to_png(target_pptx_path)
            else:
                print(f"Skipping existing PPTX: {target_pptx_path}")

def transcript_if_necessary(source_version_path):
    subfolders = [f for f in os.listdir(source_version_path) if os.path.isdir(os.path.join(source_version_path, f)) and "-DNT" not in f]
    for subfolder in sorted(subfolders):
        subfolder_path = os.path.join(source_version_path, subfolder)
        source_slide_path = os.path.join(subfolder_path, 'slides')

        if os.path.isdir(source_slide_path):
            files = os.listdir(source_slide_path)
            txt_files = [os.path.splitext(f)[0] for f in files if f.endswith('.txt')]
            mp3_files = [os.path.splitext(f)[0] for f in files if f.endswith('.mp3')]

            missing_transcripts = set(mp3_files) - set(txt_files)
            if missing_transcripts:
                model = TranscriptionModel(source_slide_path)
                for file in tqdm(missing_transcripts, desc=f"Transcribing audio for {subfolder}", unit="file"):
                    audio_path = f"{source_slide_path}/{file}.mp3"
                    model.load_and_transcribe_audio(audio_path)

def translate_transcripts(source_version_path, target, target_version_path):
    subfolders = [f for f in os.listdir(source_version_path) if os.path.isdir(os.path.join(source_version_path, f)) and "-DNT" not in f]
    for subfolder in sorted(subfolders):
        subfolder_path = os.path.join(source_version_path, subfolder)
        source_slide_path = os.path.join(subfolder_path, 'slides')
        if os.path.isdir(source_slide_path):
            target_slide_path = os.path.join(target_version_path, subfolder, 'slides')
            os.makedirs(target_slide_path, exist_ok=True)

            txt_files = [f for f in os.listdir(source_slide_path) if f.endswith('.txt')]
            for filename in tqdm(txt_files, desc=f"Translating transcripts for {subfolder}", unit="file"):
                source_file_path = os.path.join(source_slide_path, filename)
                target_file_path = os.path.join(target_slide_path, filename)

                if not os.path.exists(target_file_path):
                    with open(source_file_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()
                    translated_content = translate_txt_to(content, target)

                    with open(target_file_path, 'w', encoding='utf-8') as target_file:
                        target_file.write(translated_content)
                else:
                    print(f"Skipping existing transcript: {target_file_path}")

def generate_translated_audios(target_version_path):
    subfolders = [f for f in os.listdir(target_version_path) if os.path.isdir(os.path.join(target_version_path, f)) and "-DNT" not in f]
    for subfolder in sorted(subfolders):
        subfolder_path = os.path.join(target_version_path, subfolder)
        target_slide_path = os.path.join(subfolder_path, 'slides')
        if os.path.isdir(target_slide_path):
            for filename in tqdm(os.listdir(target_slide_path), desc=f"Generating audio for {subfolder}", unit="file"):
                if filename.endswith('.txt'):
                    voice = filename.split('.')[-2].split('_')[-1]
                    filepath = f"{target_slide_path}/{filename}"
                    audio_filepath = f"{target_slide_path}/{os.path.splitext(filename)[0]}.mp3"
                    if not os.path.exists(audio_filepath):
                        text_to_speech(filepath, voice_ids[voice])
                    else:
                        print(f"Skipping existing audio: {audio_filepath}")

def generate_translated_videos(target_version_path):
    subfolders = [f for f in os.listdir(target_version_path) if os.path.isdir(os.path.join(target_version_path, f)) and "-DNT" not in f]
    subfolders = sorted(subfolders)
    for subfolder in tqdm(subfolders, desc=f"Generating videos", unit="folder"):
        subfolder_path = os.path.join(target_version_path, subfolder)
        target_slide_path = os.path.join(subfolder_path, 'slides')
        if os.path.isdir(target_slide_path):
            video_path = os.path.join(subfolder_path, f"{subfolder}.mp4")
            if not os.path.exists(video_path):
                create_video(target_slide_path, video_path)
            else:
                print(f"Skipping existing video: {video_path}")

if __name__ == "__main__":
    print("Welcome to the Course, Language, and Version Selection Tool")
    print_separator("=")
    
    selected_dir = select_directory()
    source, targets = select_languages(selected_dir)
    source_version = select_source_version(selected_dir, source)
    
    print("\nSelection Summary:")
    print_separator()
    print(f"Selected directory : {selected_dir}")
    print(f"Source language   : {language_codes[source]} ({source})")
    print(f"Source version    : {source_version}")
    print("Target languages  :")
    for target in targets:
        print(f"                   {language_codes[target]} ({target})")
    print_separator()
    
    source_version_path = os.path.join(selected_dir, source, source_version)
    target_version_paths = prepare_target_folders(selected_dir, source, targets, source_version)
    for i, target in enumerate(targets):
        target_version_path = target_version_paths[i]
        
        print(f"\nProcessing target language: {language_codes[target]} ({target})")
        print_separator()

        translate_pptx_in_subfolders(source_version_path, source, target_version_path, target)
        
        transcript_if_necessary(source_version_path)
        translate_transcripts(source_version_path, target, target_version_path)
        
        generate_translated_audios(target_version_path)
        generate_translated_videos(target_version_path)
        
        print(f"Completed processing for {language_codes[target]} ({target})")
        print_separator()

    print("\nTranslation process completed for all target languages.")
    print_separator("=")
