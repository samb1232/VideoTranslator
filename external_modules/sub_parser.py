import json
import re
from datetime import datetime, timedelta


class Subtitle:
    def __init__(self, id: int, start_time: int, end_time: int, text: str, speaker: str | None = None):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.speaker = speaker
        self.text = text

    def __repr__(self):
        return f"Subtitle(number={self.id}, start_time={self.start_time}, end_time={self.end_time}, duration={self.duration}, speaker={self.speaker}, text={self.text})"


MIN_GAP_BETWEEN_SUBS_IN_SECS = timedelta(seconds=0.5)
MAX_SUB_TEXT_LENGTH_IN_SYMBOLS = 250


def correct_subtitles_length(subs_arr) -> str:
    new_subs_arr = []
    index = 0
    i = 0
    while i < len(subs_arr):
        current_sub = subs_arr[i]
        if i + 1 < len(subs_arr):
            next_sub = subs_arr[i + 1]
            gap = next_sub.start_time - current_sub.end_time
            tex_len = len(current_sub.text) + len(next_sub.text)
            if gap <= MIN_GAP_BETWEEN_SUBS_IN_SECS and tex_len <= MAX_SUB_TEXT_LENGTH_IN_SYMBOLS:
                # Concat subtitles
                new_start_time = current_sub.start_time
                new_end_time = next_sub.end_time
                new_text = current_sub.text + ' ' + next_sub.text
                index += 1
                new_subtitle = Subtitle(
                    id=index, 
                    start_time=new_start_time, 
                    end_time=new_end_time, 
                    text=new_text
                    )
                new_subs_arr.append(new_subtitle)
                i += 2
                continue

        index += 1
        new_subtitle = Subtitle(
            id=index, 
            start_time=current_sub.start_time, 
            end_time=current_sub.end_time,
            text=current_sub.text
            )
        new_subs_arr.append(new_subtitle)
        i += 1

    new_subs_arr = fix_subtitles_sentenses(new_subs_arr)

    srt_output = convert_subs_arr_to_srt(new_subs_arr)
    return srt_output


def fix_subtitles_sentenses(subs_arr):
    for i in range(1, len(subs_arr)-1):
        current_text = subs_arr[i].text
        previous_text = subs_arr[i-1].text

        # Checking if there are sentence fragments in the current subtitle
        if re.search(r'[.!?]', current_text):
            sentences = re.split(r'([.!?])', current_text)
            # Concat sentences and punctuation
            last_sentence = sentences[-1]
            sentences = [sentences[i] + sentences[i+1] for i in range(0, len(sentences)-1, 2)]
            if len(last_sentence) > 1:
                sentences.append(last_sentence)

            if len(sentences) > 1 and len(sentences[0].split()) < 4 and not re.search(r'[.!?]$', previous_text):
                # Move the first sentence to the previous subtitle
                subs_arr[i-1].text = previous_text + ' ' + sentences[0]
                subs_arr[i].text = ' '.join(sentences[1:])
    return subs_arr

def convert_subs_arr_to_srt(subs_arr: list):
    srt_output = ""
    for sub in subs_arr:
        srt_output += f"{sub.id}\n"
        srt_output += f"{format_time_ms_to_str(sub.start_time)} --> {format_time_ms_to_str(sub.end_time)}\n"
        srt_output += f"{sub.text}\n\n"
    return srt_output
    

def write_subs_arr_to_srt_file(subs_arr: list, output_file_path: str):
    srt_string_out = convert_subs_arr_to_srt(subs_arr)
    with open(output_file_path, "w", encoding="utf-8") as f_out:
        f_out.write(srt_string_out)


def write_subs_arr_to_json_file(subtitles, filename):
    subtitles_dict = [subtitle_to_dict(subtitle) for subtitle in subtitles]
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(subtitles_dict, file, ensure_ascii=False, indent=4)


def parse_json_to_subtitles(json_filename: str):
    with open(json_filename, 'r', encoding='utf-8') as file:
        subtitles_data = json.load(file)

    subtitles = []
    for data in subtitles_data:
        start_time = parse_time_str_to_ms(data['start'])
        end_time = parse_time_str_to_ms(data['end'])
        subtitle = Subtitle(
            id=data['id'],
            start_time=start_time,
            end_time=end_time,
            text=data['text'],
            speaker=data['speaker']
        )
        subtitles.append(subtitle)

    return subtitles


def subtitle_to_dict(subtitle: Subtitle):
    return {
        "id": subtitle.id,
        "start": format_time_ms_to_str(subtitle.start_time),
        "end": format_time_ms_to_str(subtitle.end_time),
        "text": subtitle.text,
        "speaker": subtitle.speaker
    }


def format_time_ms_to_str(time_ms: int, for_srt: bool = False):
    milliseconds = time_ms % 1000
    seconds = (time_ms // 1000) % 60
    minutes = (time_ms // (1000 * 60)) % 60
    hours = time_ms // (1000 * 60 * 60)
    ms_sep = "," if for_srt else "."
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def parse_time_str_to_ms(time_str: str):
    """Takes a time string in the format "HH:MM:SS,mmm" and converts it to a total number of milliseconds."""
    hours, minutes, seconds_milliseconds = time_str.split(':')
    seconds, milliseconds = map(int, seconds_milliseconds.split(','))
    total_ms = int(hours) * 3600000 + int(minutes) * 60000 + seconds * 1000 + milliseconds
    return total_ms


def parse_srt_to_arr_from_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        subtitles_str = file.read()

    return parse_srt_to_arr(subtitles_str)


def parse_srt_to_arr(subtitles_srt_string: str):
    subtitles = []
    lines = subtitles_srt_string.splitlines()

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
        start_time_ms = parse_time_str_to_ms(start_time_str)
        end_time_ms = parse_time_str_to_ms(end_time_str)

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
