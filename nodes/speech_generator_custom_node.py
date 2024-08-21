import os
from pydub import AudioSegment
import torch
from TTS.api import TTS
from audiostretchy.stretch import stretch_audio
import shutil


from external_modules.sub_parser import parse_srt_to_arr_from_file

class SpeechGeneratorCustomNode:
    PATH_TO_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
    # PATH_TO_MODEL = "tts_models/en/multi-dataset/tortoise-v2"
    BASE_TEMP_FOLDER_NAME = "temp"

    def __init__(self, language: str = None, speaker_ex_voice_wav_file: str = None) -> None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("device:" + device)
        self.tts = TTS(model_name=self.PATH_TO_MODEL).to(device)
        self.lang = language
        self.speaker_ex_voice_wav_file = speaker_ex_voice_wav_file

        if not os.path.exists(self.BASE_TEMP_FOLDER_NAME):
            os.makedirs(self.BASE_TEMP_FOLDER_NAME)
       

    def _synthesize(self, text_to_speak: str, out_wav_file_path: str):
        self.tts.tts_to_file(text=text_to_speak, 
                             speaker_wav=self.speaker_ex_voice_wav_file, 
                             language=self.lang, 
                             file_path=out_wav_file_path)

    def _adjust_audio_speed(self, input_audio_path: str, output_audio_path: str, target_duration: int):
        audio = AudioSegment.from_file(input_audio_path)
        current_duration = len(audio)
        speed_ratio = target_duration * 1000 / current_duration
        #Correct speed ratio in case of errors
        if speed_ratio < 0.2:
            speed_ratio = 1.0
        elif speed_ratio > 2.9:
            speed_ratio = 2.9
        
        stretch_audio(input_audio_path, output_audio_path, ratio=speed_ratio)

    def _merge_audios(self, subtitles, output_file_name):
        last_sub_end_time = subtitles[-1].end_time
        full_audio_length = last_sub_end_time.hour * 3600000 + last_sub_end_time.minute * 60000 + (last_sub_end_time.second + 1) * 1000

        final_audio = AudioSegment.silent(duration=full_audio_length)

        for subtitle in subtitles:
            audio_file = f"{self.path_to_temp_folder}/{subtitle.number}_adj.wav"
            if not os.path.exists(audio_file):
                continue

            audio_segment = AudioSegment.from_wav(audio_file)
            start_time_ms = int(
                subtitle.start_time.hour * 3600000 + subtitle.start_time.minute * 60000 + subtitle.start_time.second * 1000 + subtitle.start_time.microsecond // 1000)

            final_audio = final_audio.overlay(audio_segment, position=start_time_ms)

        final_audio.export(output_file_name, format="wav")

    def synthesise_full_audio(self, path_to_srt_subs: str, output_file_path: str):
        temp_folder_name = "temp_for_" + os.path.split(path_to_srt_subs)[1].split(".")[-2]
        self.path_to_temp_folder = os.path.join(self.BASE_TEMP_FOLDER_NAME, temp_folder_name)
        if not os.path.exists(self.path_to_temp_folder):
            os.makedirs(self.path_to_temp_folder)

        subtitles_arr = parse_srt_to_arr_from_file(path_to_srt_subs)
        cnt = 1
        last = len(subtitles_arr)
        for subtitle in subtitles_arr:
            print(f"Progress: {cnt}/{last}")
            cnt += 1
            path_to_subtitle = f"{self.path_to_temp_folder}/{subtitle.number}.wav"
            path_to_subtitle_adj = f"{self.path_to_temp_folder}/{subtitle.number}_adj.wav"

            self._synthesize(subtitle.text,  path_to_subtitle)
            self._adjust_audio_speed(path_to_subtitle,
                                     path_to_subtitle_adj,
                                     subtitle.duration 
                                     )
        
        
        self._merge_audios(subtitles_arr, output_file_path)
        shutil.rmtree(self.path_to_temp_folder)
