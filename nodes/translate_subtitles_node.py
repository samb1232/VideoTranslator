from external_modules.ts_translator import TranslateSubtitle, Translators


class TranslateSubtitlesNode:
    def __init__(self,
                 src_lang: str,
                 target_lang: str,
                 translator_type: Translators = Translators.google,
                 out_dir_name: str = "translation_results") -> None:
        self.ts = TranslateSubtitle(out_dir_name, translator_type, src_lang, target_lang)

    def translate_srt(self, src_file_path: str):
        self.ts.subtitle_translator(src_file_path)
