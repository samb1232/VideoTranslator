import time
from deep_translator import GoogleTranslator

import backend.config as config
from modules.utilities import sub_parser
from modules.utilities.my_yandex_translator import MyYandexTranslator


class Translators:
    google = 'google'
    yandex = 'yandex'


class SubsTranslator:
    TRANSLATION_LIMIT = 5000

    def __init__(self, translator: Translators, source_lang, target_lang, end_line_separator) -> None:
        self.translator = translator
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.end_line_separator = end_line_separator

        if translator == 'google':
            self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
        elif translator == 'yandex':
            self.translator = MyYandexTranslator(
                api_key=config.YA_TRANSLATE_API_KEY, 
                folder_id=config.YA_TRANSLATE_FOLDER_ID,
                src_lang=self.source_lang,
                dest_lang=self.target_lang
                )

    def translate_srt_file(self, input_file_path: str, output_file_path: str):
        """
        Translate a subtitle .SRT file from original language to desired language.
        """
        subs_arr = sub_parser.parse_srt_to_arr_from_file(input_file_path)
        subs_translated_arr = self._translate_subtitles(subs_arr, self.TRANSLATION_LIMIT, self.end_line_separator)
        sub_parser.write_subs_arr_to_srt_file(subs_translated_arr, output_file_path)

        print("New file: ", output_file_path)

    def translate_json_file(self, input_file_path: str, output_file_path: str):
        """
        Translate a subtitle .JSON file from original language to desired language.
        """
        subs_arr = sub_parser.parse_json_to_subtitles(input_file_path)
        subs_translated_arr = self._translate_subtitles(subs_arr, self.TRANSLATION_LIMIT, self.end_line_separator)
        sub_parser.write_subs_arr_to_json_file(subs_translated_arr, output_file_path)

        print("New file: ", output_file_path)

    def _parse_text_to_arr(self, text: str):
        final_arr = text.split("\n\n")
        return final_arr[:-1]

    def _translate_subtitles(self, subs_arr, translation_limit, end_line_separator):
        """
        Translate a list of subtitles from original language to desired language.

        :param subs_arr: List of subtitle objects to translate.
        :param translation_limit: Maximum length of text to translate at once.
        :param end_line_separator: Separator to use between subtitles.
        :return: List of translated subtitle objects.
        """
        text_translatable = ""
        subs_translated_arr = []
        translated_subs_counter = 0

        for sub_index in range(len(subs_arr) + 1):
            is_last = sub_index == len(subs_arr)
            if not is_last:
                sub_text = subs_arr[sub_index].text
            else:
                sub_text = ""

            if (len(text_translatable) + len(sub_text) + len(end_line_separator) * 60 >= translation_limit) or (
                is_last and len(text_translatable) > 0):
                translated_text = self.translator.translate(text_translatable).replace(end_line_separator, "")
                translated_arr = self._parse_text_to_arr(translated_text)

                translated_arr_correct_len = sub_index - translated_subs_counter
                if len(translated_arr) != translated_arr_correct_len:
                    print(f"WARNING: incorrect translation: translated_arr len is {len(translated_arr)}, but should be {translated_arr_correct_len}")

                for i in range(len(translated_arr)):
                    old_sub = subs_arr[translated_subs_counter + i]
                    new_sub = sub_parser.Subtitle(
                        id=old_sub.id,
                        speaker=old_sub.speaker,
                        start_time=old_sub.start_time,
                        end_time=old_sub.end_time,
                        text=translated_arr[i]
                    )
                    subs_translated_arr.append(new_sub)

                text_translatable = ""
                translated_subs_counter = sub_index
                if not is_last:
                    time.sleep(5)

            text_translatable += sub_text + end_line_separator + "\n\n"

        return subs_translated_arr
