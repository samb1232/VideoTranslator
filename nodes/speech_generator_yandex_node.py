import os

import librosa
import soundfile as sf
import pysndfx
from pysndfx import AudioEffectsChain

from pydub import AudioSegment

from speechkit import model_repository, configure_credentials, creds

from config import YA_SPEECHKIT_API_KEY
from external_modules.sub_parser import parse_srt_to_arr_from_file


class VoicesFemale:
    julia: str = "julia"
    alena: str = "alena"
    jane: str = "jane"
    omazh: str = "omazh"
    dasha: str = "dasha"
    lera: str = "lera"
    masha: str = "masha"
    marina: str = "marina"


class VoicesMale:
    filipp: str = "filipp"
    ermil: str = "ermil"
    madirus: str = "madirus"
    zahar: str = "zahar"
    alexander: str = "alexander"
    kirill: str = "kirill"
    anton: str = "anton"


class SpeechGeneratorYandexNode:
    """Module for synthesising subtitle to voice"""

    TEMP_OUT_FOLDER_NAME = "temp_out"

    def __init__(self, model_voice: str, model_role: str = "neutral"):
        if not os.path.exists(self.TEMP_OUT_FOLDER_NAME):
            os.makedirs(self.TEMP_OUT_FOLDER_NAME)

        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=YA_SPEECHKIT_API_KEY
            )
        )
        self.model = model_repository.synthesis_model()
        self.model.voice = model_voice
        if model_role != "":
            self.model.role = model_role

        self.sr_sum = 0
        self.sr_count = 0

    def _synthesize_and_adjust(self, text_to_speak: str, target_duration: float, export_filename: str):
        self.model.speed = 1.0
        result = self.model.synthesize(text_to_speak, raw_format=False)
        current_duration = len(result)
        speed_ratio = current_duration / (target_duration * 1000)

        #Correct speed ratio in case of errors
        if speed_ratio < 0.2:
            speed_ratio = 1.0
        elif speed_ratio > 2.9:
            speed_ratio = 2.9

        if abs(1-speed_ratio) > 0.1:
            self.model.speed = speed_ratio
            result = self.model.synthesize(text_to_speak, raw_format=False)


        result.export(f"{self.TEMP_OUT_FOLDER_NAME}/{export_filename}", 'wav')

    # @staticmethod
    # def _adjust_audio_speed(audio_path, target_duration, output_path):
    #     y, sr = librosa.load(audio_path, sr=None)
    #     current_duration = librosa.get_duration(y=y, sr=sr)
    #     speed_ratio = current_duration / target_duration
    #     y_stretched = librosa.effects.time_stretch(y, rate=speed_ratio)
    #     sf.write(output_path, y_stretched, sr)

    # @staticmethod
    # def _adjust_audio_speed(audio_path, target_duration, output_path):
    #     y, sr = sf.read(audio_path)
    #     current_duration = len(y) / sr
    #     speed_ratio = current_duration / target_duration
    #     fx = AudioEffectsChain().speed(speed_ratio)
    #     y_changed = fx(y)
    #     sf.write(output_path, y_changed, sr)

    def _adjust_audio_speed(self, audio_path, target_duration, output_path):
        audio_segment = AudioSegment.from_wav(audio_path)
        current_duration = len(audio_segment)
        speed_ratio = current_duration / (target_duration * 1000)

        self.sr_sum += speed_ratio
        self.sr_count += 1

        if speed_ratio > 1.05:
            new_audio = audio_segment.speedup(playback_speed=speed_ratio)
        else:
            new_audio = audio_segment
        new_audio.export(output_path, format="wav")


    def _merge_audios(self, full_audio_length, subtitles, output_file_name):

        final_audio = AudioSegment.silent(duration=full_audio_length)

        for subtitle in subtitles:
            audio_file = f"{self.TEMP_OUT_FOLDER_NAME}/{subtitle.number}.wav"
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
            self._synthesize_and_adjust(subtitle.text, subtitle.duration, f"{subtitle.number}.wav")
            # self._adjust_audio_speed(f"{self.TEMP_OUT_FOLDER_NAME}/{subtitle.number}.wav", 
            #                          subtitle.duration, 
            #                          f"{self.ADJUSTED_OUT_FOLDER_NAME}/adj_{subtitle.number}.wav")
        
        self._merge_audios(final_audio_len, subtitles_arr, output_file_path)
        # print("Avg speed_adjustment:", self.sr_sum/self.sr_count)
    