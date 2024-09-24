import os
import re
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def create_video(directory, output_path):
    files = sorted(os.listdir(directory), key=lambda x: [int(i) for i in re.split(r'\.|_', x) if i.isdigit()])
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    audio_files = [f for f in files if f.lower().endswith('.mp3')]

    if len(image_files) == len(audio_files):
        clips = create_clips_equal(directory, image_files, audio_files)
    elif len(image_files) == len(audio_files) + 1:
        clips = create_clips_unequal(directory, image_files, audio_files)
    else:
        raise ValueError("Invalid number of images and audio files. Should be either equal or N images and N-1 audio files.")

    if not clips:
        raise ValueError("No valid clips were created. Check your input files.")

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec='libx264', fps=1.0, threads=6)

def create_clips_equal(directory, image_files, audio_files):
    clips = []
    for img, aud in zip(image_files, audio_files):
        image_path = os.path.join(directory, img)
        audio_path = os.path.join(directory, aud)
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = get_audio_duration(audio_clip, aud)
            video_clip = ImageClip(image_path).set_duration(audio_duration).set_audio(audio_clip)
            clips.append(video_clip)
        except Exception as e:
            print(f"Error processing {img} and {aud}: {str(e)}")
    return clips

def create_clips_unequal(directory, image_files, audio_files):
    clips = []
    # Handle the first two images and first audio file specially
    first_image = ImageClip(os.path.join(directory, image_files[0]))
    second_image = ImageClip(os.path.join(directory, image_files[1]))
    first_audio = AudioFileClip(os.path.join(directory, audio_files[0]))
    first_audio_part = first_audio.subclip(0, 3)
    second_audio_part = first_audio.subclip(3)
    
    first_clip = first_image.set_duration(3).set_audio(first_audio_part)
    clips.append(first_clip)
    second_clip = second_image.set_duration(second_audio_part.duration).set_audio(second_audio_part)
    clips.append(second_clip)
    
    # Process the rest of the images and audio files
    for img, aud in zip(image_files[2:], audio_files[1:]):
        image_path = os.path.join(directory, img)
        audio_path = os.path.join(directory, aud)
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = get_audio_duration(audio_clip, aud)
            video_clip = ImageClip(image_path).set_duration(audio_duration).set_audio(audio_clip)
            clips.append(video_clip)
        except Exception as e:
            print(f"Error processing {img} and {aud}: {str(e)}")
    return clips

def get_audio_duration(audio_clip, audio_file):
    if audio_clip.duration is None or audio_clip.duration == 0:
        print(f"Warning: Audio file {audio_file} has no duration. Using default duration of 5 seconds.")
        return 5.0
    return float(audio_clip.duration)

