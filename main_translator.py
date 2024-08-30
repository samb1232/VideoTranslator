from nodes.translate_subtitles_node import TranslateSubtitlesNode, Translators

translator_node = TranslateSubtitlesNode(Translators.yandex, "en", "ru", " //")

translator_node.translate_srt_file("test_files\\0000\\0000_en.srt", "test_files\\0000\\0000_ru.srt")
