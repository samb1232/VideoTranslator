from nodes.subtitles_generator_node import VoceToSubtitlesNode
from external_modules.ts_translator import Translators
from nodes.translate_subtitles_node import TranslateSubtitlesNode

def create_subs_from_video(in_file_path: str, out_file_path: str, src_lang: str):
    voice_node = VoceToSubtitlesNode(src_lang)
    voice_node.transcript(in_file_path, out_file_path)

def translate_subs(in_file_path: str, out_file_path: str, src_lang: str, targ_lang: str):
    translator_node = TranslateSubtitlesNode(Translators.yandex, " //")
    translator_node.translate_srt(in_file_path, out_file_path, src_lang, targ_lang)
