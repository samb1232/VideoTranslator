from nodes.subtitles_generator_node import VoceToSubtitlesNode

voice_node = VoceToSubtitlesNode("en")

voice_node.transcript("test_files\\4\\cand4.mp4", "test_files\\4\\cand4_subs.srt")
