from external_modules.ts_translator import Translators
from nodes.translate_subtitles_node import TranslateSubtitlesNode

translator_node = TranslateSubtitlesNode(Translators.google, "materials")
# for i in range(1, 11):
#     translator_node.translate_srt(f"materials/{i}_subs_eng.srt", "en", "ru")
#     translator_node.translate_srt(f"materials/{i}_subs_eng.srt", "en", "es")

translator_node.translate_srt(f"materials/{8}_subs_eng.srt", "en", "ru")
# translator_node.translate_srt(f"materials/{6}_subs_eng.srt", "en", "es")
