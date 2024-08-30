from nodes.speech_generator_custom_node import SpeechGeneratorCustomNode


sg_node = SpeechGeneratorCustomNode(language="ru", 
                                    speaker_ex_voice_wav_file="test_files\\voices_samples\\female_2.wav")
sg_node.synthesise_full_audio(path_to_srt_subs="test_files\\0017\\DUROV_TEXT_RU.srt", 
                              output_file_path='test_files\\0017\\DUROV_TEXT_RU_1.wav')
print("Done!")
