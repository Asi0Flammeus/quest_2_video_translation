import sys
import os
import re
import yaml

# Root directory
ROOT_DIR = "../test/"  # Replace this with your actual root directory path

language_codes = {
    "cs": "Czech", "de": "German", "en": "English", "es": "Spanish",
    "et": "Estonian", "fi": "Finnish", "fr": "French", "id": "Indonesian",
    "it": "Italian", "ja": "Japanese", "pt": "Portuguese", "ru": "Russian",
    "vi": "Vietnamese", "zh-Hans": "Simplified Chinese"
}

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
            # Create new version for existing language
            existing_versions = [d for d in os.listdir(target_lang_path) if re.match(r'v\d{3}', d)]
            if not existing_versions:
                new_version = 'v001'
            else:
                latest_version = max(existing_versions)
                new_version_num = int(latest_version[1:]) + 1
                new_version = f'v{new_version_num:03d}'
            
            new_version_path = os.path.join(target_lang_path, new_version)
            target_version_paths.append(new_version_path)
            os.makedirs(new_version_path)
            
            # Copy structure from source_version
            source_version_path = os.path.join(course_dir, source_lang, source_version)
            copy_folder_structure(source_version_path, new_version_path)
            print(f"Created new version {new_version} for {target_lang}")
    return target_version_paths

def translate_pptx_in_subfolders(source_version_path, source, target_version_path, target):
    for subfolder in os.listdir(source_version_path):
        subfolder_path = os.path.join(source_version_path, subfolder)
        if os.path.isdir(subfolder_path):
            pptx_file = f"{subfolder}.pptx"
            source_pptx_path = os.path.join(subfolder_path, pptx_file)

            if os.path.exists(source_pptx_path):
                target_subfolder_path = os.path.join(target_version_path, subfolder)
                os.makedirs(target_subfolder_path, exist_ok=True)
                target_pptx_path = os.path.join(target_subfolder_path, pptx_file)

                #translate_pptx(source_pptx_path, target_pptx_path)
                # export_pptx(target_pptx_path)

                print(f"Translated {pptx_file} from {source} to {target}")


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
    
    # Prepare target folders
    source_version_path = f"{selected_dir}/{source}/{source_version}"
    target_version_paths = prepare_target_folders(selected_dir, source, targets, source_version)
    for i , target in enumerate(targets):
        translate_pptx_in_subfolders(source_version_path, source, target_version_paths[i], target)

        # transcript if necessary the source mp3
        # translate transcripts 
        # generate audio 
    

    print("Target folders have been prepared.")
    print("Thank you for using the selection tool!")
