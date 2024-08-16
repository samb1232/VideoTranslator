from nodes.speech_generator_custom_node import SpeechGeneratorCustomNode


sg_node = SpeechGeneratorCustomNode(language="ru", 
                                    speaker_ex_voice_wav_file="test_files\\voices_samples\\male_1.wav")
sg_node.synthesise_full_audio(src_audio_path="test_files\\0010\\audio_0010.wav", 
                              path_to_srt_subs="test_files\\0010\\0010_subs_en_ru_yandex.srt", 
                              output_file_path='test_files\\0010\\0010_RU.wav')
print("Done!")
