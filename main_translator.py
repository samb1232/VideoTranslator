from external_modules.ts_translator import Translators
from nodes.translate_subtitles_node import TranslateSubtitlesNode

translator_node = TranslateSubtitlesNode(Translators.yandex, "test_files\\4_tehnik", " //")

translator_node.translate_srt("test_files\\4_tehnik\\tehnik_subs.srt", "ru", "en")
