from external_modules.ts_translator import TranslateSubtitle, Translators


class TranslateSubtitlesNode:
    def __init__(self,
                 translator_type: Translators = Translators.google,
                 out_dir_name: str = "translation_results") -> None:
        self.translator_type = translator_type
        self.out_dir_name = out_dir_name

    def translate_srt(self, input_src_file_path: str, src_lang: str, target_lang: str):
        ts = TranslateSubtitle(self.out_dir_name, self.translator_type, src_lang, target_lang)
        ts.translate_src_file(input_src_file_path)
