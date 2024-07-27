import os

from pydub import AudioSegment
from speechkit import model_repository, configure_credentials, creds

from config import YA_SPEECHKIT_API_KEY
from external_modules.sub_parser import parse_srt_to_arr


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


class SpeechGeneratorNode:
    """Module for synthesising subtitle to voice"""

    TEMP_OUT_FOLDER_NAME = "temp_out"

    def __init__(self, full_video_length: float, model_voice: str, model_role: str = "neutral",
                 model_speed: float = 1.0):
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=YA_SPEECHKIT_API_KEY
            )
        )
        self.model = model_repository.synthesis_model()
        self.model.voice = model_voice
        self.model.role = model_role
        self.model.speed = model_speed
        self.full_video_length = full_video_length

    def _synthesize(self, text_to_speak: str, export_file_path: str):
        result = self.model.synthesize(text_to_speak, raw_format=False)
        result.export(export_file_path, 'wav')

    @staticmethod
    def _change_audio_speed(audio_segment, target_duration):
        current_duration = len(audio_segment)
        speed_ratio = target_duration / current_duration
        return audio_segment.speedup(playback_speed=1 / speed_ratio)

    def _merge_audios(self, subtitles, output_file_name):
        final_audio = AudioSegment.silent(duration=self.full_video_length)

        for subtitle in subtitles:
            audio_file = f"{self.TEMP_OUT_FOLDER_NAME}/{subtitle.number}.wav"
            if not os.path.exists(audio_file):
                continue

            audio_segment = AudioSegment.from_wav(audio_file)
            target_duration = int(subtitle.duration.total_seconds() * 1000)  # pydub works in milliseconds
            adjusted_audio = self._change_audio_speed(audio_segment, target_duration)
            start_time_ms = int(
                subtitle.start_time.hour * 3600000 + subtitle.start_time.minute * 60000 + subtitle.start_time.second * 1000 + subtitle.start_time.microsecond // 1000)

            final_audio = final_audio.overlay(adjusted_audio, position=start_time_ms)

        final_audio.export(output_file_name, format="wav")

    def synthesise_full_audio(self, path_to_srt_subs: str, output_file_path: str):
        subtitles_arr = parse_srt_to_arr(path_to_srt_subs)
        for subtitle in subtitles_arr:
            self._synthesize(subtitle.text, f"{self.TEMP_OUT_FOLDER_NAME}/{subtitle.number}.wav")

        self._merge_audios(subtitles_arr, output_file_path)


if __name__ == "__main__":
    sg_node = SpeechGeneratorNode(15, VoicesFemale.omazh)
    sg_node._synthesize("",
                        "test_aaudio.wav")
    