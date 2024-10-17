import os
import re
import psutil
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip

def limit_resources():
    # Get the current process
    current_process = psutil.Process()
    # Set the resource limits to a % of the machine's capacity
    factor = 0.50
    ram_limit = psutil.virtual_memory().total * factor 
    cpu_limit = psutil.cpu_count() * factor
    # Set the resource limits for the current process
    current_process.rlimit(psutil.RLIMIT_AS, (ram_limit, ram_limit))
    current_process.cpu_affinity([int(cpu) for cpu in range(int(cpu_limit))])

def create_video(directory, output_path):
    limit_resources()
    files = sorted(os.listdir(directory), key=lambda x: [int(i) for i in re.split(r'\.|_', x) if i.isdigit()])
    image_files = [f for f in files if f.lower().endswith(('.png'))]
    audio_files = [f for f in files if f.lower().endswith('.mp3')]

    if len(image_files) == len(audio_files):
        clips = []
        for img, aud in zip(image_files, audio_files):
            image_path = os.path.join(directory, img)
            audio_path = os.path.join(directory, aud)
            audio_clip = AudioFileClip(audio_path)
            silent_clip = AudioFileClip.silent(duration=0.5)
            extended_audio = concatenate_audioclips([audio_clip, silent_clip])
            video_clip = ImageClip(image_path).set_duration(extended_audio.duration).set_audio(extended_audio)
            clips.append(video_clip)
    else:
        raise ValueError("Invalid number of images and audio files. Should be equal.")

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec='libx264', fps=1.0, threads=4, ffmpeg_params=['-preset', 'ultrafast', '-crf', '28'])
    final_clip.close()
    for clip in clips:
        clip.close()
