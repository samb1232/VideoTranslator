from nodes.speech_generator_custom_node import SpeechGeneratorCustomNode


sg_node = SpeechGeneratorCustomNode(language="ru", 
                                    speaker_ex_voice_wav_file="test_files\\voices_samples\\female_1.wav")
sg_node.synthesise_full_audio(src_audio_path="test_files\\0004\\audio_0004.wav", 
                              path_to_srt_subs="test_files\\0004\\0004_FIXED.srt", 
                              output_file_path='test_files\\0004\\0004_ru_fixed.wav')
print("Done!")
