from nodes.subtitles_generator_node import VoceToSubtitlesNode

voice_node = VoceToSubtitlesNode("ru")

voice_node.transcript("test_files\\4_tehnik\\tehnik_vid.mp4", "test_files\\4_tehnik\\tehnik_subs.srt")
