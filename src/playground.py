from mp3_2_txt import TranscriptionModel 

model = TranscriptionModel("../test/")
path = "../test/test.mp3"
model.load_and_transcribe_audio(path)
