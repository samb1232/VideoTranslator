import os
from pydub import AudioSegment
import torch
from TTS.api import TTS
from audiostretchy.stretch import stretch_audio

from modules.utilities import audio_injector
from modules.utilities.sub_parser import parse_json_to_subtitles, export_subtitles_to_json_file
from modules.utilities.voice_extractor import extract_speaker_voices


class VoiceGenerator:
    PATH_TO_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
    BASE_TEMP_FOLDER_NAME = os.path.join("uploads", "temp")

    def __init__(self, language: str = None) -> None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("device:" + device)
        self.tts = TTS(model_name=self.PATH_TO_MODEL,progress_bar=False).to(device)
        self.lang = language

        os.makedirs(self.BASE_TEMP_FOLDER_NAME, exist_ok=True)
       
    def _synthesize(self, text_to_speak: str, speaker_ex_wav_filename: str, out_wav_filepath: str):
        self.tts.tts_to_file(text=text_to_speak, 
                             speaker_wav=speaker_ex_wav_filename, 
                             language=self.lang, 
                             file_path=out_wav_filepath)

    def _adjust_audio_speed(self, input_audio_path: str, output_audio_path: str, target_duration: int):
        audio = AudioSegment.from_file(input_audio_path)
        current_duration = len(audio)
        speed_ratio = target_duration / current_duration
        # Correct speed ratio in case of errors
        if speed_ratio < 0.2:
            speed_ratio = 1.0
        elif speed_ratio > 2.9:
            speed_ratio = 2.9
        
        stretch_audio(input_audio_path, output_audio_path, ratio=speed_ratio)

    def _merge_audios(self, subtitles, output_file_name):
        last_sub_end_time = subtitles[-1].end_time
        full_audio_length = last_sub_end_time + 1000

        final_audio = AudioSegment.silent(duration=full_audio_length)

        for subtitle in subtitles:
            audio_file = f"{self.path_to_temp_folder}/{subtitle.id}_adj.wav"
            if not os.path.exists(audio_file):
                continue

            audio_segment = AudioSegment.from_wav(audio_file)

            final_audio = final_audio.overlay(audio_segment, position=subtitle.start_time)

        final_audio.export(output_file_name, format="wav")

    def generate_audio(self, orig_wav_filepath: str,  json_subs_filepath: str, out_wav_filepath: str):
        temp_folder_name = "temp_" + os.path.split(json_subs_filepath)[1].split(".")[-2]
        self.path_to_temp_folder = os.path.join(self.BASE_TEMP_FOLDER_NAME, temp_folder_name)
        os.makedirs(self.path_to_temp_folder, exist_ok=True)

        subtitles_arr = parse_json_to_subtitles(json_subs_filepath)
        temp_speakers_folder = os.path.join(self.path_to_temp_folder, "speakers_wav")
        speakers_voices = extract_speaker_voices(
            audio_filepath=orig_wav_filepath,
            subtitles=subtitles_arr,
            out_folder=temp_speakers_folder
        )

        cnt = 1
        last = len(subtitles_arr)
        for subtitle in subtitles_arr:
            print(f"Progress: {cnt}/{last}")
            cnt += 1
            path_to_subtitle = f"{self.path_to_temp_folder}/{subtitle.id}.wav"
            path_to_subtitle_adj = f"{self.path_to_temp_folder}/{subtitle.id}_adj.wav"
            path_to_speaker_ex = speakers_voices[subtitle.speaker]

            if not subtitle.modified and os.path.exists(path_to_subtitle_adj):
                print("Skipping...")
                continue

            self._synthesize(subtitle.text, path_to_speaker_ex, path_to_subtitle)

            self._adjust_audio_speed(path_to_subtitle,
                                     path_to_subtitle_adj,
                                     subtitle.duration 
                                     )
            subtitle.modified = False
        
        export_subtitles_to_json_file(subtitles_arr, json_subs_filepath)

        self._merge_audios(subtitles_arr, out_wav_filepath)
        

    @staticmethod
    def replace_audio_in_video(in_audio_path: str, in_video_path: str, out_video_path: str):
        audio_injector.replace_audio_in_video(in_audio_path, in_video_path, out_video_path, "200k")