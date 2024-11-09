import json
import re
from typing import List

from assemblyai import Utterance


class Subtitle:
    def __init__(self, id: int, start_time: int, end_time: int, text: str, speaker: str | None = None, modified: bool = True):
        self.id: int = id
        self.start_time: int = start_time
        self.end_time: int = end_time
        self.duration: int = end_time - start_time
        self.speaker: str | None = speaker
        self.text: str = text
        self.modified: bool = modified

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
        
        if len(sub["text"]) == 0:
            return False

        time_pattern = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}$')
        if not isinstance(sub["start"], str) or not time_pattern.match(sub["start"]):
            return False

        if not isinstance(sub["end"], str) or not time_pattern.match(sub["end"]):
            return False

    return True


def split_utterances_to_subtitles(utterances: List[Utterance]) -> List[Subtitle]:
    """
    Splits an utterances into multiple parts if the pause between sentences exceeds MAX_PAUSE_DURATION_MS.
    
    :param utterances: The list of Utterance objects to split.
    :return: A list of Subtitles.
    """
    MAX_PAUSE_BETWEEN_WORDS_MS = 1000
    MAX_SYMBOLS_PER_SUBTITLE = 200
    END_SENTENCE_SYMBOLS = ".?;:!"
    id_counter = 1
    subtitles_arr = []
    
    for utterance in utterances:
        sentences_len_arr = get_sentences_len_from_text(text=utterance.text,  end_sentence_symbols=END_SENTENCE_SYMBOLS)
        sentence_counter = 0
        words_arr = utterance.words
        
        
        current_subtitle = Subtitle(
            id=id_counter,
            start_time=words_arr[0].start,
            end_time=words_arr[0].end,
            speaker=utterance.speaker,
            text=words_arr[0].text
        )
        for i in range(1, len(words_arr)):
            pause_between_words = words_arr[i].start - words_arr[i-1].end
            is_end_of_sentence = words_arr[i-1].text[-1] in END_SENTENCE_SYMBOLS
            condition_pause = pause_between_words > MAX_PAUSE_BETWEEN_WORDS_MS
            condition_end_sentence = is_end_of_sentence and len(current_subtitle.text) > MAX_SYMBOLS_PER_SUBTITLE
            condition_next_sentence_too_big = is_end_of_sentence and (
                sentence_counter + 1 < len(sentences_len_arr)) and (
                sentences_len_arr[sentence_counter + 1] > MAX_SYMBOLS_PER_SUBTITLE - len(current_subtitle.text)
                )
            condition_sentence_too_big = len(current_subtitle.text) > 2 * MAX_SYMBOLS_PER_SUBTITLE
            
            if is_end_of_sentence:
                sentence_counter += 1
            
            if condition_pause or condition_end_sentence or condition_next_sentence_too_big or condition_sentence_too_big:
                # Finalize the current subtitle
                subtitles_arr.append(current_subtitle)
                id_counter += 1
                # Start a new subtitle
                current_subtitle = Subtitle(
                    id=id_counter,
                    start_time=words_arr[i].start,
                    end_time=words_arr[i].end,
                    speaker=utterance.speaker,
                    text=words_arr[i].text
                    )
            else:
                # Continue the current utterance
                current_subtitle.text += " " + words_arr[i].text
                current_subtitle.end_time = words_arr[i].end

        # Add the last subtitle
        subtitles_arr.append(current_subtitle)
        id_counter += 1

    return subtitles_arr


def get_sentences_len_from_text(text: str, end_sentence_symbols: str) -> List[int]:
    """
    Splits the input text into sentences and returns a list of the lengths of each sentence.
    """
    sentence_end_pattern = f"[{re.escape(end_sentence_symbols)}]"
    sentences = re.split(sentence_end_pattern, text)
    sentence_lengths = [len(sentence.strip()) for sentence in sentences if sentence.strip()]
    return sentence_lengths
