import os
from typing import List
from pydub import AudioSegment

from shared_utils.sub_parser import Subtitle


def extract_speaker_voices_from_audio(audio_filepath: str, subtitles: List[Subtitle], out_folder_name = "speakers"):
    os.makedirs(out_folder_name, exist_ok=True)

    max_duration_subtitles = _find_subtitle_for_each_speaker(subtitles)

    audio = AudioSegment.from_wav(audio_filepath)

    # Create audio for each speakers
    speaker_audio_paths = {}
    for speaker, subtitle in max_duration_subtitles.items():
        speaker_audio = _create_audio_for_speaker(audio, subtitle)

        output_file_path = os.path.join(out_folder_name, f"{speaker}.wav")
        speaker_audio.export(output_file_path, format="wav")

        speaker_audio_paths[speaker] = output_file_path

    return speaker_audio_paths


def _find_subtitle_for_each_speaker(subtitles: List[Subtitle]) -> dict:
    max_duration_subtitles = {}

    for subtitle in subtitles:
        if subtitle.speaker is None:
            continue
        
        if subtitle.speaker not in max_duration_subtitles:
            max_duration_subtitles[subtitle.speaker] = subtitle
        elif subtitle.duration > max_duration_subtitles[subtitle.speaker].duration:
            max_duration_subtitles[subtitle.speaker] = subtitle
                
    return max_duration_subtitles


def _create_audio_for_speaker(src_audio: AudioSegment, speaker_subtitle: Subtitle) -> AudioSegment:
    SUBTITLE_MAX_DURATION_MS = 60000
    
    start_time = speaker_subtitle.start_time
    end_time = speaker_subtitle.end_time
    
    if speaker_subtitle.duration > SUBTITLE_MAX_DURATION_MS:
        end_time = start_time + SUBTITLE_MAX_DURATION_MS

    trimmed_audio = src_audio[start_time:end_time]
    return trimmed_audio
