import re
from datetime import datetime


class Subtitle:
    def __init__(self, number, start_time, end_time, duration, text):
        self.number = number
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.text = text

    def __repr__(self):
        return f"Subtitle(number={self.number}, start_time={self.start_time}, end_time={self.end_time}, duration={self.duration}, text={self.text})"


def parse_srt_to_arr(file_path):
    subtitles = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

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
        duration = end_time - start_time

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

