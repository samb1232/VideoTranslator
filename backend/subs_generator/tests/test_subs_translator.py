import json
import os
import shutil
import unittest
from unittest.mock import patch

from shared_utils.sub_parser import Subtitle
from subs_translator import SubsTranslator, Translators


class TestSubsTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = SubsTranslator(
            translator=Translators.google,
            source_lang='es',
            target_lang='en'
        )
        
        self.temp_folder = "temp_t"
        os.makedirs(self.temp_folder)
    
    
    def tearDown(self):
        if os.path.exists(self.temp_folder):
            shutil.rmtree(self.temp_folder) 
        
        
    def test_parse_text_to_arr_multiple_lines(self):
        text = "Line 1\n\nLine 2\n\nLine 3"
        result = self.translator._parse_text_to_arr(text)
        self.assertEqual(result, ["Line 1", "Line 2", "Line 3"])
        
        
    def test_parse_text_to_arr_with_linebreak_in_the_end(self):
        text = "Line 1\n\nLine 2\n\nLine 3\n\n"
        result = self.translator._parse_text_to_arr(text)
        self.assertEqual(result, ["Line 1", "Line 2", "Line 3"])
        
        
    def test_parse_text_to_arr_single_line(self):
        text = "Line 1"
        result = self.translator._parse_text_to_arr(text)
        self.assertEqual(result, ["Line 1"])
        
        
    def test_parse_text_to_arr_empty(self):
        text = ""
        result = self.translator._parse_text_to_arr(text)
        self.assertEqual(result, [])
        
        
    @patch('deep_translator.GoogleTranslator.translate')
    def test_translate_subtitles(self, mock_translate):
        mock_translate.return_value = "Translated text 1 //\n\nTranslated text 2"

        subtitles = [
            Subtitle(id=1, speaker="Speaker 1", start_time=10, end_time=1000, text="Text 1"),
            Subtitle(id=2, speaker="Speaker 2", start_time=1010, end_time=2000, text="Text 2")
        ]

        result = self.translator._translate_subtitles(subtitles, 1000000, " //")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].text, "Translated text 1")
        self.assertEqual(result[1].text, "Translated text 2")
    
    
    @patch('deep_translator.GoogleTranslator.translate')
    def test_translate_srt_file(self, mock_translate):
        mock_translate.return_value = "Hello world"
        temp_srt_path = os.path.join(self.temp_folder, "temp_srt.srt")
        temp_output_path = os.path.join(self.temp_folder, "temp_out.srt")
        with open(temp_srt_path, "w") as temp_srt:
            temp_srt.write("1\n00:00:01,000 --> 00:00:04,000\nHola Mundo\n\n") 
        
        self.translator.translate_srt_file(temp_srt_path, temp_output_path)
        
        with open(temp_output_path, 'r') as f:
            content = f.read()
            self.assertIn("1\n00:00:01,000 --> 00:00:04,000\nHello world\n\n", content)


    @patch('deep_translator.GoogleTranslator.translate')
    def test_translate_json_file(self, mock_translate):
        mock_translate.return_value = "Hello world"
        temp_json_path = os.path.join(self.temp_folder, "temp_srt.json")
        temp_output_path = os.path.join(self.temp_folder, "temp_out.json")

        with open(temp_json_path, "w") as temp_json:
            temp_json.write('[{"id": 1, "modified": false, "speaker": "Speaker 1", "start": "00:00:01,000", "end": "00:00:04,000", "text": "Hola Mundo"}]')
        
        self.translator.translate_json_file(temp_json_path, temp_output_path)

        with open(temp_output_path, 'r') as f:
            content = json.load(f)
            self.assertEqual(content[0]['text'], "Hello world")

