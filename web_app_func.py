from nodes.subtitles_generator_node import VoceToSubtitlesNode
from external_modules.ts_translator import Translators
from nodes.translate_subtitles_node import TranslateSubtitlesNode
from nodes.speech_generator_custom_node import SpeechGeneratorCustomNode

def create_subs_from_video(in_file_path: str, out_file_path: str, src_lang: str):
    voice_node = VoceToSubtitlesNode(src_lang)
    voice_node.transcript(in_file_path, out_file_path)
    print("DONE!")

def translate_subs(in_file_path: str, out_file_path: str, src_lang: str, targ_lang: str):
    translator_node = TranslateSubtitlesNode(Translators.yandex, " //")
    translator_node.translate_srt(in_file_path, out_file_path, src_lang, targ_lang)
    print("DONE!")

def generate_voice(src_lang: str, speaker_ex_filepath: str, subs_filepath: str, out_filepath: str):
    sg_node = SpeechGeneratorCustomNode(language=src_lang, 
                                    speaker_ex_voice_wav_file=speaker_ex_filepath)
    sg_node.synthesise_full_audio(path_to_srt_subs=subs_filepath, 
                                output_file_path=out_filepath)
    print("DONE!")
