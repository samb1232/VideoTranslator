from modules.subs_generator import SubsGenerator

voice_node = SubsGenerator("en")

voice_node.transcript("backend\\test_files\\0004\\0004.mp4",  "backend\\test_files\\0004")


print("DONE!")