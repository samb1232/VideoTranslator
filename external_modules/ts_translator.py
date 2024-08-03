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

TRANSLATION_LIMIT = 4500


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
    def __init__(self, out_dir, translator, source_lang, target_lang) -> None:
        self.out_dir = out_dir
        self.translator = translator
        self.source_lang = source_lang
        self.target_lang = target_lang

    @staticmethod
    def read_file_as_list(file_name):
        fr = codecs.open(file_name, "r", encoding='utf-8-sig')
        lines = fr.read()
        fr.close()

        # some SRTs such as created by whisper doesn't have \r\n but some other have it
        if "\r\n" in lines:
            return lines.split("\r\n\r\n")
        if "\n\n" in lines:
            return lines.split("\n\n")

    def format_file_name(self, file_name):
        file_name = file_name.split("/")[-1].split("\\")[-1]
        # Check if the directory already exists
        if not os.path.exists(self.out_dir):
            # If it doesn't exist, create the directory
            os.makedirs(self.out_dir)
            print(f"Translation folder created at: {self.out_dir}")

        name_sep = f'translated-{self.target_lang}-{self.translator}'

        # index number of last dot
        last_dot = file_name.rfind('.')

        # means that there is no dot in the file name, 
        # and file name has no file type extension 
        if last_dot == -1:
            new_file_name = self.out_dir + file_name + str(name_sep) + '.srt'
        else:
            base_name = file_name[0: last_dot]
            ext = file_name[last_dot: len(file_name)]
            new_file_name = self.out_dir + '/' + base_name + "-" + str(name_sep) + ext
        return new_file_name

    def translate_src_file(self, input_file_path):
        """
        this function translate a subtitle file from original language to desired language
        
        line may be the order number of the subtitle or just for real line 
        such as answer to age given "33" or there is no order number but "-->"   
        must be present to in the middle of the start and end time of subtitle
        to be shown. There must an empty line between two ordered subtitle.
        Expected /standard subtitle should be like this:
            1
            00:00:27,987 --> 00:00:29,374
            - Babe.
            - Mmm.
            
            2
            00:00:30,210 --> 00:00:31,634
            - Lizzie.
            - Mmm.
            
            3
        """

        content_list = self.read_file_as_list(input_file_path)
        durations = []
        contents = []
        text_translatable = ''

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
            translator = YandexTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'papago':
            translator = PapagoTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'deepl':
            translator = DeeplTranslator(source=self.source_lang, target=self.target_lang)

        elif self.translator == 'qcri':
            translator = QcriTranslator(source=self.source_lang, target=self.target_lang)

        number_of_translatable_content = len(content_list)

        for c in range(number_of_translatable_content):
            lines = []
            # some SRTs such as created by whisper doesn't have \r\n but some other have it

            lines = content_list[c].split("\n")
            assert len(lines) == 3 or len(lines) == 1

            time_info = ''
            text_info = ''
            for i in range(len(lines)):
                if i < len(lines) - 1 and lines[i].rstrip().isdigit() and "-->" in lines[i + 1] or "-->" in lines[i]:
                    time_info += lines[i] + "\r\n"
                    continue
                else:
                    text_info += lines[i] + " (КОФ)\n"

                    # list doesn't have the value at number_of_translatable_content index
            if len(text_translatable) + len(text_info) > TRANSLATION_LIMIT or c == number_of_translatable_content - 1:
                try:
                    translated_sub = translator.translate(text_translatable).replace(" (КОФ)", "")
                    temp_translated = translated_sub.replace("\n\n", "\n").replace("\n", "\n\n\r")

                    temp_translated = temp_translated.split("\n\r")
                    temp_translated[-1] = temp_translated[-1] + "\n"
                    contents += temp_translated
                except TypeError as err:
                    print(err)

                text_translatable = text_info
                durations.append(time_info)
                time.sleep(5)
            else:
                durations.append(time_info)
                text_translatable += text_info + "\n\r"

        with open(self.format_file_name(input_file_path), 'w', encoding='utf-8') as out_file:
            for d, c in zip(durations, contents):
                out_file.write(d.replace('\r\r', ''))
                out_file.write(c + "\n")
                # print(d + c)

        print("Done!")
        print("New file name: ", self.format_file_name(input_file_path))
