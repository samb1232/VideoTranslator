import re
from datetime import datetime, timedelta


class Subtitle:
    def __init__(self, number, start_time, end_time, duration, text):
        self.number = number
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.text = text

    def __repr__(self):
        return f"Subtitle(number={self.number}, start_time={self.start_time}, end_time={self.end_time}, duration={self.duration}, text={self.text})"


def parse_srt_to_arr(subtitles_str: str):
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

        start_time_str, end_time_str = time_match.groups()
        start_time = datetime.strptime(start_time_str, '%H:%M:%S,%f')
        end_time = datetime.strptime(end_time_str, '%H:%M:%S,%f')
        duration_td = end_time - start_time
        duration = duration_td.total_seconds()

        text = []
        i += 2
        while i < len(lines) and lines[i].strip() != '':
            text.append(lines[i].strip())
            i += 1

        text = '\n'.join(text)
        subtitle = Subtitle(number, start_time, end_time, duration, text)
        subtitles.append(subtitle)
        i += 1

    return subtitles


def parse_srt_to_arr_from_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        subtitles_str = file.read()

    return parse_srt_to_arr(subtitles_str)


MIN_GAP_BETWEEN_SUBS_IN_SECS = timedelta(seconds=0.5)
MAX_SUB_TEXT_LENGTH_IN_SYMBOLS = 250


def correct_subtitles_length(subtitles: str) -> str:
    subs_arr = parse_srt_to_arr(subtitles)
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
                new_duration_td = new_end_time - new_start_time
                new_duration = new_duration_td.total_seconds()



                new_text = current_sub.text + ' ' + next_sub.text
                index += 1
                new_subtitle = Subtitle(index, new_start_time, new_end_time, new_duration, new_text)
                new_subs_arr.append(new_subtitle)
                i += 2
                continue

        index += 1
        new_subtitle = Subtitle(index, current_sub.start_time, current_sub.end_time, current_sub.duration,
                                current_sub.text)
        new_subs_arr.append(new_subtitle)
        i += 1

    # Преобразуем новый массив субтитров обратно в строку формата SRT
    srt_output = ""
    for sub in new_subs_arr:
        srt_output += f"{sub.number}\n"
        srt_output += f"{sub.start_time.strftime('%H:%M:%S,%f')[:-3]} --> {sub.end_time.strftime('%H:%M:%S,%f')[:-3]}\n"
        srt_output += f"{sub.text}\n\n"

    return srt_output
