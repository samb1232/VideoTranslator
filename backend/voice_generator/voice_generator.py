import os
import time
from typing import List
import torch
from audiostretchy.stretch import stretch_audio
from pydub import AudioSegment
from TTS.api import TTS
from logging_conf import setup_logging
from utils import audio_worker
from utils.voice_extractor import extract_speaker_voices_from_audio
from shared_utils.sub_parser import Subtitle, parse_json_to_subtitles, export_subtitles_to_json_file

logger = setup_logging()

class VoiceGenerator:
    PATH_TO_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
    BASE_TEMP_FOLDER_NAME = os.path.join("uploads", "temp")

    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initialazing voice generator on device: {device}")
        self.tts = TTS(model_name=self.PATH_TO_MODEL,progress_bar=False).to(device)

        os.makedirs(self.BASE_TEMP_FOLDER_NAME, exist_ok=True)
    
    def generate_audio(self, orig_wav_filepath: str, language: str, json_subs_filepath: str, out_wav_filepath: str):
        self.path_to_temp_folder = self._generate_temp_folder(json_subs_filepath)

        subtitles = parse_json_to_subtitles(json_subs_filepath)
        temp_speakers_folder = os.path.join(self.path_to_temp_folder, "speakers_wav")
        speakers_voices = extract_speaker_voices_from_audio(
            audio_filepath=orig_wav_filepath,
            subtitles=subtitles,
            out_folder_name=temp_speakers_folder
        )

        cnt = 1
        last_subtitle_index = len(subtitles)
        for subtitle in subtitles:
            logger.debug(f"Progress: {cnt}/{last_subtitle_index}. Synthesysing text: \"{subtitle.text}\"")
            cnt += 1
            
            path_to_subtitle = f"{self.path_to_temp_folder}/{subtitle.id}.wav"
            path_to_subtitle_adj = f"{self.path_to_temp_folder}/{subtitle.id}_adj.wav"
            path_to_speaker_ex = speakers_voices[subtitle.speaker]

            if not subtitle.modified and os.path.exists(path_to_subtitle_adj):
                logger.debug(f"Skipping...")
                continue

            self._synthesize_text(
                text_to_speak=subtitle.text, 
                speaker_ex_wav_filename=path_to_speaker_ex, 
                out_wav_filepath=path_to_subtitle, 
                lang=language
                )
            self._adjust_audio_speed(
                input_audio_path=path_to_subtitle,
                output_audio_path=path_to_subtitle_adj,
                target_duration=subtitle.duration 
                )
            subtitle.modified = False
        
        export_subtitles_to_json_file(subtitles, json_subs_filepath)

        self._merge_audios(subtitles, out_wav_filepath)
        
    def _generate_temp_folder(self, subs_filepath: str) -> str:
        temp_folder_name = "temp_" + os.path.split(subs_filepath)[1].split(".")[-2]
        path_to_temp_folder = os.path.join(self.BASE_TEMP_FOLDER_NAME, temp_folder_name)
        os.makedirs(path_to_temp_folder, exist_ok=True)
        return path_to_temp_folder
           
    def _synthesize_text(self, text_to_speak: str, speaker_ex_wav_filename: str, out_wav_filepath: str, lang: str):
        if len(text_to_speak) == 0:
            raise KeyError("Error. Text to speak is empty")
        self.tts.tts_to_file(text=text_to_speak, 
                             speaker_wav=speaker_ex_wav_filename, 
                             language=lang, 
                             file_path=out_wav_filepath)
        time.sleep(0.1)

    def _adjust_audio_speed(self, input_audio_path: str, output_audio_path: str, target_duration: int):
        audio = AudioSegment.from_file(input_audio_path)
        current_duration = len(audio)
        speed_ratio = target_duration / current_duration
        
        # Set warnings in bad cases
        if speed_ratio < 0.2:
            logger.warning(f"Speed ratio is too low: {speed_ratio}. Result may be bad.")
        elif speed_ratio > 2.5:
            logger.warning(f"Speed ratio is too high: {speed_ratio}. Result may be bad.")
        
        stretch_audio(input_audio_path, output_audio_path, ratio=speed_ratio)

    def _merge_audios(self, subtitles: List[Subtitle], output_filepath: str):
        last_sub_end_time = subtitles[-1].end_time
        full_audio_length = last_sub_end_time + 1000 # add 1 second of silence at the end

        final_audio = AudioSegment.silent(duration=full_audio_length)

        for subtitle in subtitles:
            audio_file = f"{self.path_to_temp_folder}/{subtitle.id}_adj.wav"
            if not os.path.exists(audio_file):
                logger.warning(f"Audio file {audio_file} is not exist.")
                continue

            audio_segment = AudioSegment.from_wav(audio_file)

            final_audio = final_audio.overlay(audio_segment, position=subtitle.start_time)

        final_audio.export(output_filepath, format="wav")

    
    @staticmethod
    def replace_audio_in_video(in_audio_path: str, in_video_path: str, out_video_path: str):
        audio_worker.inject_audio_in_video(in_audio_path, in_video_path, out_video_path, "200k")