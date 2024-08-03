from nodes.speech_generator_node import SpeechGeneratorNode, VoicesFemale

sg_node = SpeechGeneratorNode(VoicesFemale.jane, "neutral", 1.2)
sg_node.synthesise_full_audio("materials\\1_audio.mp3","materials\\1_subs_eng-translated-ru-google.srt", 'audio_merged.wav')
print("Done!")
