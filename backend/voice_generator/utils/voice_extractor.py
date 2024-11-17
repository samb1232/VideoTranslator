import os
from pydub import AudioSegment


def extract_speaker_voices(audio_filepath, subtitles, out_folder = "speakers"):
    os.makedirs(out_folder, exist_ok=True)

    max_duration_subtitles = {}

    # Find the subtitles with the longest duration for each speaker
    for subtitle in subtitles:
        if subtitle.speaker:
            if subtitle.speaker not in max_duration_subtitles:
                max_duration_subtitles[subtitle.speaker] = subtitle
            elif subtitle.duration > max_duration_subtitles[subtitle.speaker].duration:
                max_duration_subtitles[subtitle.speaker] = subtitle

    audio = AudioSegment.from_wav(audio_filepath)

    # Create audio for each speakers
    speaker_audio_paths = {}
    for speaker, subtitle in max_duration_subtitles.items():
        start_time = subtitle.start_time
        end_time = subtitle.end_time

        if subtitle.duration > 60000:
            end_time = start_time + 60000

        # Trim audio
        speaker_audio = audio[start_time:end_time]

        output_file_path = os.path.join(out_folder, f"{speaker}.wav")
        speaker_audio.export(output_file_path, format="wav")

        speaker_audio_paths[speaker] = output_file_path

    return speaker_audio_paths