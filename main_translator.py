from external_modules.ts_translator import Translators
from nodes.translate_subtitles_node import TranslateSubtitlesNode

translator_node = TranslateSubtitlesNode("en", "ru", Translators.google)
translator_node.translate_srt("subs-generated.srt")
