import pytest
from flask_api.utils.sub_parser import Subtitle, export_subtitles_to_srt_file, export_subtitles_to_json_file, parse_json_to_subtitles, parse_srt_to_subtitles, format_time_ms_to_str, format_time_str_to_ms, check_json_subs_format


def test_subtitle_initialization():
    subtitle = Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A")
    assert subtitle.id == 1
    assert subtitle.start_time == 1000
    assert subtitle.end_time == 2000
    assert subtitle.duration == 1000
    assert subtitle.speaker == "A"
    assert subtitle.text == "Hello, world!"
    assert subtitle.modified is True


def test_subtitle_to_dict():
    subtitle = Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A")
    expected_dict = {
        "id": 1,
        "start": "00:00:01,000",
        "end": "00:00:02,000",
        "text": "Hello, world!",
        "speaker": "A",
        "modified": True,
    }
    assert subtitle.to_dict() == expected_dict


def test_export_subtitles_to_srt_file(tmp_path):
    subtitles = [
        Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A"),
        Subtitle(id=2, start_time=3000, end_time=4000, text="Goodbye, world!", speaker="B"),
    ]
    output_file = tmp_path / "subtitles.srt"
    export_subtitles_to_srt_file(subtitles, output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    expected_content = "1\n00:00:01,000 --> 00:00:02,000\nHello, world!\n\n2\n00:00:03,000 --> 00:00:04,000\nGoodbye, world!\n\n"
    assert content == expected_content


def test_export_subtitles_to_json_file(tmp_path):
    subtitles = [
        Subtitle(id=1, start_time=1000, end_time=2000, text="Hello, world!", speaker="A"),
        Subtitle(id=2, start_time=3000, end_time=4000, text="Goodbye, world!", speaker="B"),
    ]
    output_file = tmp_path / "subtitles.json"
    export_subtitles_to_json_file(subtitles, output_file)
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
    assert content.strip() == expected_content.strip()


def test_parse_json_to_subtitles(tmp_path):
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
    json_file = tmp_path / "subtitles.json"
    with open(json_file, "w", encoding="utf-8") as f:
        f.write(json_content)
    subtitles = parse_json_to_subtitles(json_file)
    assert len(subtitles) == 2
    assert subtitles[0].id == 1
    assert subtitles[0].start_time == 1000
    assert subtitles[0].end_time == 2000
    assert subtitles[0].text == "Hello, world!"
    assert subtitles[0].speaker == "A"
    assert subtitles[0].modified is True
    assert subtitles[1].id == 2
    assert subtitles[1].start_time == 3000
    assert subtitles[1].end_time == 4000
    assert subtitles[1].text == "Goodbye, world!"
    assert subtitles[1].speaker == "B"
    assert subtitles[1].modified is True


def test_parse_srt_to_subtitles(tmp_path):
    srt_content = "1\n00:00:01,000 --> 00:00:02,000\nHello, world!\n\n2\n00:00:03,000 --> 00:00:04,000\nGoodbye, world!\n\n"
    srt_file = tmp_path / "subtitles.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_content)
    subtitles = parse_srt_to_subtitles(srt_file)
    assert len(subtitles) == 2
    assert subtitles[0].id == 1
    assert subtitles[0].start_time == 1000
    assert subtitles[0].end_time == 2000
    assert subtitles[0].text == "Hello, world!"
    assert subtitles[1].id == 2
    assert subtitles[1].start_time == 3000
    assert subtitles[1].end_time == 4000
    assert subtitles[1].text == "Goodbye, world!"


@pytest.mark.parametrize(
    "int_num, str_num",
    [
        (1000, "00:00:01,000"), 
        (3600000, "01:00:00,000"), 
        (3661000, "01:01:01,000"),
        ]
)
def test_format_time_ms_to_str(int_num, str_num):
    assert format_time_ms_to_str(int_num) == str_num

@pytest.mark.parametrize(
    "str_num, int_num",
    [
        ("00:00:01,000", 1000), 
        ("01:00:00,000", 3600000), 
        ("01:01:01,000", 3661000),
        ]
)
def test_format_time_str_to_ms(str_num, int_num):
    assert format_time_str_to_ms(str_num) == int_num


def test_check_json_subs_format():
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
    assert check_json_subs_format(valid_subs) is True
    assert check_json_subs_format(invalid_subs) is False
