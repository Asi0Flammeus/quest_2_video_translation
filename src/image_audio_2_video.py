import os
import re
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import gc

def calculate_chunk_size(directory, audio_files, target_chunk_duration=60, max_chunk_size=10):
    """
    Calculate the optimal chunk size based on audio durations or file sizes.
    
    :param directory: Directory containing the audio files
    :param audio_files: List of audio file names
    :param target_chunk_duration: Target duration for each chunk in seconds
    :param max_chunk_size: Maximum allowed chunk size
    :return: Calculated chunk size
    """
    total_duration = 0
    total_size = 0

    for audio_file in audio_files:
        file_path = os.path.join(directory, audio_file)
        try:
            with AudioFileClip(file_path) as audio:
                total_duration += audio.duration
            total_size += os.path.getsize(file_path)
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")

    # Calculate chunk size based on duration
    chunk_size_duration = max(1, min(max_chunk_size, int(len(audio_files) * target_chunk_duration / total_duration)))
    
    # Calculate chunk size based on file size (assuming 1MB per minute of audio as a rough estimate)
    avg_size_per_file = total_size / len(audio_files)
    target_chunk_size = target_chunk_duration * 1024 * 1024 / 60  # Convert minutes to bytes
    chunk_size_filesize = max(1, min(max_chunk_size, int(target_chunk_size / avg_size_per_file)))

    # Use the smaller of the two calculated chunk sizes
    return min(chunk_size_duration, chunk_size_filesize)

def create_video(directory, output_path, target_chunk_duration=60, max_chunk_size=10):
    files = sorted(os.listdir(directory), key=lambda x: [int(i) for i in re.split(r'\.|_', x) if i.isdigit()])
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    audio_files = [f for f in files if f.lower().endswith('.mp3')]

    chunk_size = calculate_chunk_size(directory, audio_files, target_chunk_duration, max_chunk_size)
    print(f"Calculated chunk size: {chunk_size}")

    if len(image_files) == len(audio_files):
        clips = create_clips_equal(directory, image_files, audio_files, chunk_size)
    elif len(image_files) == len(audio_files) + 1:
        clips = create_clips_unequal(directory, image_files, audio_files, chunk_size)
    else:
        raise ValueError("Invalid number of images and audio files. Should be either equal or N images and N-1 audio files.")

    final_clip = None
    for i, chunk in enumerate(clips):
        print(f"Processing chunk {i+1}")
        if final_clip is None:
            final_clip = chunk
        else:
            final_clip = concatenate_videoclips([final_clip, chunk])
        
        # Clear memory
        chunk.close()
        gc.collect()

    if final_clip is None:
        raise ValueError("No valid clips were created. Check your input files.")

    print("Writing final video file")
    final_clip.write_videofile(output_path, codec='libx264', fps=1.0, threads=4)
    final_clip.close()

def create_clips_equal(directory, image_files, audio_files, chunk_size):
    clips = []
    for i, (img, aud) in enumerate(zip(image_files, audio_files)):
        image_path = os.path.join(directory, img)
        audio_path = os.path.join(directory, aud)
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = get_audio_duration(audio_clip, aud)
            video_clip = ImageClip(image_path).set_duration(audio_duration).set_audio(audio_clip)
            clips.append(video_clip)

            # Process in chunks to manage memory
            if (i + 1) % chunk_size == 0:
                yield concatenate_videoclips(clips)
                for clip in clips:
                    clip.close()
                clips = []
                gc.collect()

        except Exception as e:
            print(f"Error processing {img} and {aud}: {str(e)}")

    if clips:
        yield concatenate_videoclips(clips)
        for clip in clips:
            clip.close()

def create_clips_unequal(directory, image_files, audio_files, chunk_size):
    clips = []
    # Handle the first two images and first audio file specially
    first_image = ImageClip(os.path.join(directory, image_files[0]))
    second_image = ImageClip(os.path.join(directory, image_files[1]))
    first_audio = AudioFileClip(os.path.join(directory, audio_files[0]))
    first_audio_part = first_audio.subclip(0, 3)
    second_audio_part = first_audio.subclip(3)
    
    first_clip = first_image.set_duration(3).set_audio(first_audio_part)
    second_clip = second_image.set_duration(second_audio_part.duration).set_audio(second_audio_part)
    clips.extend([first_clip, second_clip])

    # Process the rest of the images and audio files
    for i, (img, aud) in enumerate(zip(image_files[2:], audio_files[1:]), start=2):
        image_path = os.path.join(directory, img)
        audio_path = os.path.join(directory, aud)
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = get_audio_duration(audio_clip, aud)
            video_clip = ImageClip(image_path).set_duration(audio_duration).set_audio(audio_clip)
            clips.append(video_clip)

            # Process in chunks to manage memory
            if (i + 1) % chunk_size == 0:
                yield concatenate_videoclips(clips)
                for clip in clips:
                    clip.close()
                clips = []
                gc.collect()

        except Exception as e:
            print(f"Error processing {img} and {aud}: {str(e)}")

    if clips:
        yield concatenate_videoclips(clips)
        for clip in clips:
            clip.close()

def get_audio_duration(audio_clip, audio_file):
    if audio_clip.duration is None or audio_clip.duration == 0:
        print(f"Warning: Audio file {audio_file} has no duration. Using default duration of 5 seconds.")
        return 5.0
    return float(audio_clip.duration)
