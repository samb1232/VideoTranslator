from modules.voice_generator import VoiceGenerator


sg = VoiceGenerator("en", "materials\\2_audio.wav")

text = "Swear test. Fuck me, this shit is fucking awersome. A fucking hate this cunt!"
sg._synthesize(text_to_speak=text, out_wav_filepath="test_swears.wav")

print("Done!")