from nodes.voice_to_subtitles_node import VoceToSubtitlesNode

voice_node = VoceToSubtitlesNode("en")
voice_node.transcript("materials/vid_audio_for_test.m4a", "subs-generated.srt")
