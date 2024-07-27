from nodes.speech_generator_node import SpeechGeneratorNode, VoicesFemale

sg_node = SpeechGeneratorNode(600000, VoicesFemale.marina, "neutral", 1.2)
sg_node.synthesise_full_audio("translation_result/subsen-to-ru-google.srt", 'audio_merged.wav')
