from modules.voice_generator import VoiceGenerator


sg_node = VoiceGenerator(language="ru")

sg_node.generate_audio(
    orig_wav_filepath="backend\\test_files\\0004\\audio_0004.wav",
    json_subs_filepath="backend\\test_files\\0004\\0004_ru.json",
    out_wav_filepath="backend\\test_files\\0004\\FINAL.wav"
)
print("Done!")
