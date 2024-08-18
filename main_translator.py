from external_modules.ts_translator import Translators
from nodes.translate_subtitles_node import TranslateSubtitlesNode

translator_node = TranslateSubtitlesNode(Translators.yandex, " //")

translator_node.translate_srt("test_files\\4\\cand4_subs.srt", "test_files\\4\\cand4_subs_ru.srt", "en", "ru")
