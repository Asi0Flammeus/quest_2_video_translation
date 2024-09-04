from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import os
import re

# Directory containing the images and audio files
directory = "../test/"

# Lists to store video clips
clips = []

# Regular expression to match files based on numbering
pattern = r'(\d+-\d+)(?:\.mp3|\.png)$'

# Read files from the directory and sort them
files = sorted(os.listdir(directory), key=lambda x: [int(i) for i in re.search(pattern, x).group(1).split('-')])

# Filter out files to ensure pairing of image and audio correctly
image_files = [f for f in files if f.endswith('.png')]
audio_files = [f for f in files if f.endswith('.mp3')]

# Check if the list of images and audios are equal to avoid mismatches
if len(image_files) != len(audio_files):
    raise ValueError("Mismatch in number of images and audio files")

# Create clips from image and audio pairs
for img, aud in zip(image_files, audio_files):
    image_path = os.path.join(directory, img)
    audio_path = os.path.join(directory, aud)
    
    # Ensure matching file names without extensions
    if img.split('.')[0] != aud.split('.')[0]:
        continue

    # Create an ImageClip and set its duration to the duration of the audio
    audio_clip = AudioFileClip(audio_path)
    video_clip = ImageClip(image_path, duration=audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    # Append the clip to the list
    clips.append(video_clip)

# Concatenate all the video clips into one video
final_clip = concatenate_videoclips(clips, method="compose")

# Write the result to a file
output_path = os.path.join(directory, 'output_video.mp4')
final_clip.write_videofile(output_path, codec='libx264', fps=24)

print(f"Video created successfully: {output_path}")

