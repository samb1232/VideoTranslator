from modules.subs_translator import SubsTranslator, Translators

translator_node = SubsTranslator(Translators.yandex, "en", "ru", " //")

translator_node.translate_json_file("test_files\\0000\\0000_en.json", "test_files\\0000\\0000_ru.json")

print("Done!")