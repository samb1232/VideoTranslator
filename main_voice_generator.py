from nodes.speech_generator_yandex_node import SpeechGeneratorYandexNode, VoicesFemale, VoicesMale

sg_node = SpeechGeneratorYandexNode("john", "")
sg_node.synthesise_full_audio("test_files\\4_tehnik\\audio_tehnik_vid.wav",
                               "test_files\\4_tehnik\\tehnik_subs-translated-en-yandex.srt", 
                               'test_files\\4_tehnik\\tehnik_audio_translated.wav')
print("Done!")
