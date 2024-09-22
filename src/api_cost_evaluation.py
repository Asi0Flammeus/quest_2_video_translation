
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
