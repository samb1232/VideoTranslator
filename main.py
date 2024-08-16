from external_modules.ts_translator import Translators
from nodes.subtitles_generator_node import VoceToSubtitlesNode
from nodes.translate_subtitles_node import TranslateSubtitlesNode
from nodes.speech_generator_custom_node import SpeechGeneratorCustomNode

src_lang = "en"
target_lang = "ru"
folder_name = "test_files\\0015"
video_file_name = "0015"

voice = "trump"

orig_subs_filename = f"{folder_name}\\{video_file_name}_subs_{src_lang}.srt"

voice_node = VoceToSubtitlesNode(src_lang)
voice_node.transcript(f"{folder_name}\\{video_file_name}.mp4", orig_subs_filename)

print("Subs extractions done!")

translator_node = TranslateSubtitlesNode(Translators.yandex, folder_name, " //")

translator_node.translate_srt(orig_subs_filename, src_lang, target_lang)

print("Translation done!")

sg_node = SpeechGeneratorCustomNode(language=target_lang, 
                                    speaker_ex_voice_wav_file=f"test_files\\voices_samples\\{voice}.wav")
sg_node.synthesise_full_audio(src_audio_path=f"{folder_name}\\audio_{video_file_name}.wav", 
                              path_to_srt_subs=f"{folder_name}\\{video_file_name}_subs_{src_lang}_{target_lang}_yandex.srt", 
                              output_file_path=f"{folder_name}\\{video_file_name}_{target_lang}.wav")
print("Dub generation done!")

print("Finish!")