from nodes.subtitles_generator_node import VoceToSubtitlesNode

voice_node = VoceToSubtitlesNode("en")

voice_node.transcript("test_files\\0000\\0000.mp4")

print("DONE!")