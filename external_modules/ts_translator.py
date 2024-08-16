import codecs
import os
import time

from deep_translator import (GoogleTranslator,
                             ChatGptTranslator,
                             MicrosoftTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             PapagoTranslator,
                             DeeplTranslator,
                             QcriTranslator)

from external_modules.my_yandex_translator import MyYandexTranslator

from external_modules import sub_parser

from external_modules.sub_parser import Subtitle
import config



class Translators:
    google = 'google'
    chatgpt = 'chatgpt'
    microsoft = 'microsoft'
    pons = 'pons'
    linguee = 'linguee'
    mymemory = 'mymemory'
    yandex = 'yandex'
    papago = 'papago'
    deepl = 'deepl'
    qcri = 'qcri'


class TranslateSubtitle:
    TRANSLATION_LIMIT = 5000

    def __init__(self, out_dir, translator, source_lang, target_lang, end_line_separator) -> None:
        self.out_dir = out_dir
        self.translator = translator
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.end_line_separator = end_line_separator

    def format_file_name(self, file_name):
        file_name = file_name.split("/")[-1].split("\\")[-1]
        # Check if the directory already exists
        if not os.path.exists(self.out_dir):
            # If it doesn't exist, create the directory
            os.makedirs(self.out_dir)
            print(f"Translation folder created at: {self.out_dir}")

        name_sep = f'_{self.target_lang}_{self.translator}'

        # index number of last dot
        last_dot = file_name.rfind('.')

        # means that there is no dot in the file name, 
        # and file name has no file type extension 
        if last_dot == -1:
            new_file_name = self.out_dir + file_name + str(name_sep) + '.srt'
        else:
            base_name = file_name[0: last_dot]
            ext = file_name[last_dot: len(file_name)]
            new_file_name = self.out_dir + '/' + base_name + str(name_sep) + ext
        return new_file_name

    def translate_src_file(self, input_file_path):
        """
        Translate a subtitle file from original language to desired language
        """

        translator = None
        if self.translator == 'google':
            translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'chatgpt':
            translator = ChatGptTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'microsoft':
            translator = MicrosoftTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'pons':
            translator = PonsTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'linguee':
            translator = LingueeTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'mymemory':
            translator = MyMemoryTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'yandex':
            translator = MyYandexTranslator(
                api_key=config.YA_TRANSLATE_API_KEY, 
                folder_id=config.YA_TRANSLATE_FOLDER_ID,
                src_lang=self.source_lang,
                dest_lang=self.target_lang
                )

        elif self.translator == 'papago':
            translator = PapagoTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'deepl':
            translator = DeeplTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'qcri':
            translator = QcriTranslator(source=self.source_lang, target=self.target_lang)

        text_translatable = ""

        subs_arr = sub_parser.parse_srt_to_arr_from_file(input_file_path)
        subs_translated_arr = []
        translated_subs_counter = 0

        for sub_index in range(len(subs_arr) + 1):
            is_last = sub_index == len(subs_arr)
            if not is_last:
                sub_text = subs_arr[sub_index].text
            else:
                sub_text = ""
            
            if (len(text_translatable) + len(sub_text) + len(self.end_line_separator) * 60 >= self.TRANSLATION_LIMIT) or (
                is_last and len(text_translatable) > 0):
                translated_text = translator.translate(text_translatable).replace(self.end_line_separator, "")
                translated_arr = self._parse_text_to_arr(translated_text)

                translated_arr_correct_len = sub_index - translated_subs_counter
                if len(translated_arr) != translated_arr_correct_len:
                    print(f"WARNING: incorrect translation: translated_arr len is {len(translated_arr)}, but should be {translated_arr_correct_len}")

                for i in range(len(translated_arr)):
                    old_sub = subs_arr[translated_subs_counter + i]
                    new_sub = Subtitle(
                        number=old_sub.number,
                        start_time=old_sub.start_time,
                        end_time=old_sub.end_time,
                        duration=old_sub.duration,
                        text=translated_arr[i]
                    )
                    subs_translated_arr.append(new_sub)
                
                text_translatable = ""
                translated_subs_counter = sub_index
                if not is_last: 
                    time.sleep(5)
            
            text_translatable += sub_text + self.end_line_separator + "\n\n"

        

        output_file_path = self.format_file_name(input_file_path)
        
        sub_parser.write_subs_arr_to_srt_file(subs_translated_arr, output_file_path)

        print("Done!")
        print("New file name: ", output_file_path)

    @staticmethod
    def _parse_text_to_arr(text: str):
        final_arr = text.split("\n\n")
        return final_arr[:-1]