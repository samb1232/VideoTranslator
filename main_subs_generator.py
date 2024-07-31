from nodes.subtitles_generator_node import VoceToSubtitlesNode

voice_node = VoceToSubtitlesNode("en")
for i in range(2, 11):
    voice_node.transcript(f"materials/{i}_audio.mp3", f"materials/{i}_subs_eng.srt")
