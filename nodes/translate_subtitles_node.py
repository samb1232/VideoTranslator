from external_modules.ts_translator import TranslateSubtitle, Translators


class TranslateSubtitlesNode:
    def __init__(self,
                 translator_type: Translators,
                 subs_sep: str) -> None:
        self.translator_type = translator_type
        self.subs_sep = subs_sep

    def translate_srt(self, in_file_path: str, out_file_path: str, src_lang: str, target_lang: str):
        ts = TranslateSubtitle(self.translator_type, src_lang, target_lang, self.subs_sep)
        ts.translate_src_file(in_file_path, out_file_path)
