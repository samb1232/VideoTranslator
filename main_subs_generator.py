from modules.subs_generator import SubsGenerator

voice_node = SubsGenerator("en")

voice_node.transcript("test_files\\0000\\0000.mp4")

print("DONE!")