from modules.subs_generator import SubsGenerator
from modules.subs_translator import SubsTranslator, Translators
from modules.voice_generator import VoiceGenerator

def create_subs_from_video(in_file_path: str, out_dir_path: str, src_lang: str):
    voice_node = SubsGenerator(src_lang)
    srt_filepath, json_filepath, audio_file_path = voice_node.transcript(in_file_path, out_dir_path)
    print("DONE!")
    return (srt_filepath, json_filepath, audio_file_path)


def translate_subs(in_file_path: str, out_file_path: str, src_lang: str, targ_lang: str):
    translator_node = SubsTranslator(Translators.yandex, src_lang, targ_lang, " //")
    translator_node.translate_json_file(in_file_path, out_file_path)
    print("DONE!")

def generate_voice(src_lang: str, speaker_ex_filepath: str, subs_filepath: str, out_filepath: str):
    # obsolete. Requires updating...
    pass
    print("DONE!")
