from modules.voice_generator import VoiceGenerator


sg_node = VoiceGenerator(language="ru")

sg_node.generate_audio(
    orig_wav_filepath="test_files\\0000\\audio_0000_en.wav",
    json_subs_filepath="test_files\\0000\\0000_ru.json",
    out_wav_filepath="test_files\\0000\\0000_ru.wav"
)
print("Done!")
