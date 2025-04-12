import unittest
from shared_utils import sub_parser as sp
import tempfile
import os


class TestSubParser(unittest.TestCase):
    def test_subtitle_initialization(self):
        subtitle = sp.Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A")
        self.assertEqual(subtitle.id, 1)
        self.assertEqual(subtitle.start_time, 1000)
        self.assertEqual(subtitle.end_time, 2000)
        self.assertEqual(subtitle.duration, 1000)
        self.assertEqual(subtitle.speaker, "A")
        self.assertEqual(subtitle.text, "Hello, world!")
        self.assertTrue(subtitle.modified)

    def test_subtitle_to_dict(self):
        subtitle = sp.Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A")
        expected_dict = {
            "id": 1,
            "start": "00:00:01,000",
            "end": "00:00:02,000",
            "text": "Hello, world!",
            "speaker": "A",
            "modified": True,
        }
        self.assertEqual(subtitle.to_dict(), expected_dict)

    def test_export_subtitles_to_srt_file(self):
        subtitles = [
            sp.Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A"),
            sp.Subtitle(id=2, start_time=3000, end_time=4000, text="Goodbye, world!", speaker="B"),
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as tmp_file:
            output_file = tmp_file.name
        sp.export_subtitles_to_srt_file(subtitles, output_file)
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        expected_content = "1\n00:00:01,000 --> 00:00:02,000\nHello, world!\n\n2\n00:00:03,000 --> 00:00:04,000\nGoodbye, world!\n\n"
        self.assertEqual(content, expected_content)
        os.remove(output_file)

    def test_export_subtitles_to_json_file(self):
        subtitles = [
            sp.Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A"),
            sp.Subtitle(id=2, start_time=3000, end_time=4000, text="Goodbye, world!", speaker="B"),
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            output_file = tmp_file.name
        sp.export_subtitles_to_json_file(subtitles, output_file)
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        expected_content = '''[
    {
        "id": 1,
        "start": "00:00:01,000",
        "end": "00:00:02,000",
        "text": "Hello, world!",
        "speaker": "A",
        "modified": true
    },
    {
        "id": 2,
        "start": "00:00:03,000",
        "end": "00:00:04,000",
        "text": "Goodbye, world!",
        "speaker": "B",
        "modified": true
    }
]'''
        self.assertEqual(content.strip(), expected_content.strip())
        os.remove(output_file)

    def test_parse_json_to_subtitles(self):
        json_content = '''[
            {
                "id": 1,
                "start": "00:00:01,000",
                "end": "00:00:02,000",
                "text": "Hello, world!",
                "speaker": "A",
                "modified": true
            },
            {
                "id": 2,
                "start": "00:00:03,000",
                "end": "00:00:04,000",
                "text": "Goodbye, world!",
                "speaker": "B",
                "modified": true
            }
        ]'''
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            json_file = tmp_file.name
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(json_content)
        subtitles = sp.parse_json_to_subtitles(json_file)
        self.assertEqual(len(subtitles), 2)
        self.assertEqual(subtitles[0].id, 1)
        self.assertEqual(subtitles[0].start_time, 1000)
        self.assertEqual(subtitles[0].end_time, 2000)
        self.assertEqual(subtitles[0].text, "Hello, world!")
        self.assertEqual(subtitles[0].speaker, "A")
        self.assertTrue(subtitles[0].modified)
        self.assertEqual(subtitles[1].id, 2)
        self.assertEqual(subtitles[1].start_time, 3000)
        self.assertEqual(subtitles[1].end_time, 4000)
        self.assertEqual(subtitles[1].text, "Goodbye, world!")
        self.assertEqual(subtitles[1].speaker, "B")
        self.assertTrue(subtitles[1].modified)
        os.remove(json_file)

    def test_format_time_ms_to_str(self):
        test_cases = [
            (1000, "00:00:01,000"),
            (3600000, "01:00:00,000"),
            (3661000, "01:01:01,000"),
        ]
        for int_num, str_num in test_cases:
            with self.subTest(int_num=int_num, str_num=str_num):
                self.assertEqual(sp.format_time_ms_to_str(int_num), str_num)

    def test_format_time_str_to_ms(self):
        test_cases = [
            ("00:00:01,000", 1000),
            ("01:00:00,000", 3600000),
            ("01:01:01,000", 3661000),
        ]
        for str_num, int_num in test_cases:
            with self.subTest(str_num=str_num, int_num=int_num):
                self.assertEqual(sp.format_time_str_to_ms(str_num), int_num)

    def test_check_json_subs_format(self):
        valid_subs = [
            {
                "id": 1,
                "start": "00:00:01,000",
                "end": "00:00:02,000",
                "text": "Hello, world!",
                "speaker": "A",
                "modified": True,
            },
            {
                "id": 2,
                "start": "00:00:03,000",
                "end": "00:00:04,000",
                "text": "Goodbye, world!",
                "speaker": "B",
                "modified": True,
            }
        ]
        invalid_subs = [
            {
                "id": 1,
                "start": "00:00:01,000",
                "end": "00:00:02,000",
                "text": "Hello, world!",
                "speaker": "AB",  # Invalid speaker format
                "modified": True,
            }
        ]
        self.assertTrue(sp.validate_json_subs_format(valid_subs))
        self.assertFalse(sp.validate_json_subs_format(invalid_subs))

