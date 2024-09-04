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
- [ ] mp3 vo -> txt vo -> txt translated -> mp3 translaled
- [x] ppt -> png
  - use of `ppt_2_png.sh`
- [ ] png + mp3 -> mp4

