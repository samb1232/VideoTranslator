import json
import re
from typing import List


class Subtitle:
    def __init__(self, id: int, start_time: int, end_time: int, text: str, speaker: str | None = None, modified: bool = True):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.speaker = speaker
        self.text = text
        self.modified = modified

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "start": format_time_ms_to_str(self.start_time),
            "end": format_time_ms_to_str(self.end_time),
            "text": self.text,
            "speaker": self.speaker,
            "modified": self.modified,
            }

    def __repr__(self):
        return f"Subtitle(number={self.id}, start_time={self.start_time}, end_time={self.end_time}, duration={self.duration}, speaker={self.speaker}, text={self.text}, modified={self.modified})"



def export_subtitles_to_srt_file(subs_arr: List[Subtitle], output_srt_filepath: str):
    srt_output = ""
    for sub in subs_arr:
        srt_output += f"{sub.id}\n"
        srt_output += f"{format_time_ms_to_str(sub.start_time)} --> {format_time_ms_to_str(sub.end_time)}\n"
        srt_output += f"{sub.text}\n\n"
    with open(output_srt_filepath, "w", encoding="utf-8") as f_out:
        f_out.write(srt_output)


def export_subtitles_to_json_file(subs_arr: List[Subtitle], output_json_filepath: str):
    subtitles_dict = get_subtitles_as_json_arr(subs_arr)
    with open(output_json_filepath, 'w', encoding='utf-8') as file:
        json.dump(subtitles_dict, file, ensure_ascii=False, indent=4)


def get_subtitles_as_json_arr(subtitles: List[Subtitle]) -> List[dict]:
    return [subtitle.to_dict() for subtitle in subtitles]


def parse_json_to_subtitles(json_filepath: str) -> List[Subtitle]:
    with open(json_filepath, 'r', encoding='utf-8') as file:
        subtitles_data = json.load(file)
    if not check_json_subs_format(subtitles_data):
        raise ValueError("Invalid JSON format for subtitles")

    subtitles = []
    for data in subtitles_data:
        start_time = format_time_str_to_ms(data['start'])
        end_time = format_time_str_to_ms(data['end'])
        subtitle = Subtitle(
            id=data['id'],
            start_time=start_time,
            end_time=end_time,
            text=data['text'],
            speaker=data['speaker'],
            modified= data['modified'] if 'modified' in data else True,
        )
        subtitles.append(subtitle)

    return subtitles


def parse_srt_to_subtitles(srt_filepath: str) -> List[Subtitle]:
    with open(srt_filepath, 'r', encoding='utf-8') as file:
        subtitles_str = file.read()

    subtitles = []
    lines = subtitles_str.splitlines()

    i = 0
    while i < len(lines):
        if not lines[i].strip().isdigit():
            i += 1
            continue

        number = int(lines[i].strip())
        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[i + 1].strip())
        if not time_match:
            i += 1
            continue

        start_time_str, end_time_str = time_match.groups()  # Find groups in the regex match
        start_time_ms = format_time_str_to_ms(start_time_str)
        end_time_ms = format_time_str_to_ms(end_time_str)

        text = []
        i += 2
        while i < len(lines) and lines[i].strip() != '':
            text.append(lines[i].strip())
            i += 1

        text = '\n'.join(text)
        subtitle = Subtitle(
            id=number, 
            start_time=start_time_ms, 
            end_time=end_time_ms,
            text=text
            )
        subtitles.append(subtitle)
        i += 1

    return subtitles


def format_time_ms_to_str(time_ms: int) -> str:
    """Takes a time string in milliseconds and converts it to str in format "HH:MM:SS,mmm"."""
    milliseconds = time_ms % 1000
    seconds = (time_ms // 1000) % 60
    minutes = (time_ms // (1000 * 60)) % 60
    hours = time_ms // (1000 * 60 * 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def format_time_str_to_ms(time_str: str) -> int:
    """Takes a time string in the format "HH:MM:SS,mmm" and converts it to a total number of milliseconds."""
    hours, minutes, seconds_milliseconds = time_str.split(':')
    seconds, milliseconds = map(int, seconds_milliseconds.split(','))
    total_ms = int(hours) * 3600000 + int(minutes) * 60000 + seconds * 1000 + milliseconds
    return total_ms


def check_json_subs_format(subs: List[dict]) -> bool:
    if not isinstance(subs, list):
        return False

    for sub in subs:
        if not isinstance(sub, dict):
            return False

        if not all(key in sub for key in ["id", "speaker", "text", "start", "end", "modified"]):
            return False

        if not isinstance(sub["id"], int):
            return False

        if not isinstance(sub["speaker"], str) or not re.match(r'^[A-Z]$', sub["speaker"]):
            return False

        if not isinstance(sub["text"], str):
            return False

        time_pattern = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}$')
        if not isinstance(sub["start"], str) or not time_pattern.match(sub["start"]):
            return False

        if not isinstance(sub["end"], str) or not time_pattern.match(sub["end"]):
            return False

    return True
