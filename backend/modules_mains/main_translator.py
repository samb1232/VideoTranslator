from modules.subs_translator import SubsTranslator, Translators

translator_node = SubsTranslator(Translators.yandex, "en", "ru", " //")

translator_node.translate_json_file("backend\\test_files\\0004\\0004_src.json", "backend\\test_files\\0004\\0004_ru.json")

print("Done!")