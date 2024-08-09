import os
from pydub import AudioSegment
import torch
from TTS.api import TTS
from audiostretchy.stretch import stretch_audio

from external_modules.sub_parser import parse_srt_to_arr_from_file

class SpeechGeneratorCustomNode:
    PATH_TO_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
    TEMP_FOLDER_NAME = "temp"
    ADJ_FOLDER_NAME = TEMP_FOLDER_NAME + "/" + "adj"
    def __init__(self, language: str, speaker_ex_voice_wav_file: str) -> None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("device:" + device)
        self.tts = TTS(model_name=self.PATH_TO_MODEL, progress_bar=False).to(device)
        self.lang = language
        self.speaker_ex_voice_wav_file = speaker_ex_voice_wav_file

        if not os.path.exists(self.TEMP_FOLDER_NAME):
            os.makedirs(self.TEMP_FOLDER_NAME)
        if not os.path.exists(self.ADJ_FOLDER_NAME):
            os.makedirs(self.ADJ_FOLDER_NAME)

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

    def _merge_audios(self, full_audio_length, subtitles, output_file_name):
        final_audio = AudioSegment.silent(duration=full_audio_length)

        for subtitle in subtitles:
            audio_file = f"{self.ADJ_FOLDER_NAME}/adj_{subtitle.number}.wav"
            if not os.path.exists(audio_file):
                continue

            audio_segment = AudioSegment.from_wav(audio_file)
            start_time_ms = int(
                subtitle.start_time.hour * 3600000 + subtitle.start_time.minute * 60000 + subtitle.start_time.second * 1000 + subtitle.start_time.microsecond // 1000)

            final_audio = final_audio.overlay(audio_segment, position=start_time_ms)

        final_audio.export(output_file_name, format="wav")

    def synthesise_full_audio(self, src_audio_path: str, path_to_srt_subs: str, output_file_path: str):
        subtitles_arr = parse_srt_to_arr_from_file(path_to_srt_subs)
        audio = AudioSegment.from_file(src_audio_path)
        final_audio_len = len(audio)

        for subtitle in subtitles_arr:
            # self._synthesize(subtitle.text, f"{self.TEMP_FOLDER_NAME}/{subtitle.number}.wav")
            self._adjust_audio_speed(f"{self.TEMP_FOLDER_NAME}/{subtitle.number}.wav", 
                                     f"{self.ADJ_FOLDER_NAME}/adj_{subtitle.number}.wav",
                                     subtitle.duration 
                                     )
        
        self._merge_audios(final_audio_len, subtitles_arr, output_file_path)
