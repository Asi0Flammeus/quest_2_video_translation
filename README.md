# The Quest to automatize the video translation of lectures

Here we define a video lecture, as a video with someone talking about a subject and using a powerpoint presentation.
This type of video is used in every chapter of any courses in PlanB Network, so there's a need to find a way to make the whole process as automated as possible.

## Video Translation workflows

- inputs: video vo + ppt vo of n slides
- process 1: extract n audios from videos vo
- process 2: translate audio
- process 3: translate ppt
- process 4: export ppt into images
- process 5: generate video from n images and n audios, both translated
- output: video translated

## Backlog

- [ ] ppt vo -> ppt translated
- [x] mp3 vo -> txt vo -> txt translated -> mp3 translaled
  - use of `audio_translator.py`
- [x] ppt -> png
  - use of `ppt_2_png.sh`
- [x] png + mp3 -> mp4
  - use f `image_audio_2_video.py`

## Requirements

- only tested on linus distribution
- for bash scripts you need this package installed
  - LibreOffice - 24.2.5.2
  - ImageMagick - 6.9.12.98
- for python scripts, just create a dedicated environnment and use the command `pip3 install -r requirements.txt` to install the required librairies

---

# Audio Translator

## Initial Goal

Develop a Python program to automatically transcribe all segmented audio files using a text-to-speech API, simply said an audio-2-audio Bot with translation in between.

## Initial Strategic Plan

- write a single file called `playground.py` for quick MVP, though constant will be placed in `config.py`
- encapsulate atomic process using simple functions
- will use `LLM-Translator` and `LLM-Scribe` if needed
- use folder `projects` to centralize all file produced
  - `/projects/project-name/audios/`: initial audio to translate
  - `/projects/project-name/transcripts/`: corresponding transcripts
  - `/projects/project-name/translations/`: corresponding translations
  - `/projects/project-name/outputs/`: audios produced with 11labs api
