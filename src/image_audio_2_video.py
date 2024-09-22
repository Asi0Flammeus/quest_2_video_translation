import os
import re
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def create_video(directory, output_path):

    files = sorted(os.listdir(directory), key=lambda x: [int(i) for i in re.split(r'\.|_', x) if i.isdigit()])
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    audio_files = [f for f in files if f.lower().endswith('.mp3')]

    if len(image_files) != len(audio_files) + 1:
        raise ValueError("Mismatch in number of images and audio files. There should be N images and N-1 audio files.")

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
            if audio_clip.duration is None or audio_clip.duration == 0:
                print(f"Warning: Audio file {aud} has no duration. Using default duration of 5 seconds.")
                audio_duration = 5.0
            else:
                audio_duration = float(audio_clip.duration)

            video_clip = ImageClip(image_path).set_duration(audio_duration).set_audio(audio_clip)
            clips.append(video_clip)
        except Exception as e:
            print(f"Error processing {img} and {aud}: {str(e)}")

    if not clips:
        raise ValueError("No valid clips were created. Check your input files.")

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec='libx264', fps=1.0, threads=8)
