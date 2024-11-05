import json
import os

from config import AAI_API_KEY
import assemblyai as aai

from modules.utilities.audio_worker import extract_audio_from_video
from modules.utilities.sub_parser import export_subtitles_to_json_file, format_time_ms_to_str, split_utterances_to_subtitles

class SubsGenerator:
    """Module for generating subtitles on original language"""

    def __init__(self, src_lang: str, num_of_speakers: int = None) -> None:
        aai.settings.api_key = AAI_API_KEY
        self.src_lang = src_lang
        self.aai_conf = aai.TranscriptionConfig(
            language_code=src_lang, 
            punctuate=True, 
            speaker_labels=True,
            speakers_expected=num_of_speakers,
            speech_model=aai.SpeechModel.nano
            )

    
    def transcript(self, video_file_path: str, output_dir: str | None = None):
        video_dir, video_filename = os.path.split(video_file_path)
        if output_dir is None:
            output_dir = video_dir
        os.makedirs(output_dir, exist_ok=True)
        
        out_filename = video_filename.split(".")[-2]
        self.audio_file_path = os.path.join(output_dir, f"{out_filename}_src.wav")

        extract_audio_from_video(video_file_path, self.audio_file_path)
        
        transcript = aai.Transcriber().transcribe(self.audio_file_path, self.aai_conf)

        # Export subtitles as srt
        subtitles = transcript.export_subtitles_srt()
        self.srt_out_filepath = os.path.join(output_dir, f"{out_filename}_src.srt")
        with open(self.srt_out_filepath, "w", encoding="utf-8") as srt_file:
            srt_file.write(subtitles)

        # Export subtitles as json
        self.json_out_filepath = os.path.join(output_dir,  f"{out_filename}_src.json")
        subs_arr = split_utterances_to_subtitles(transcript.utterances)
        export_subtitles_to_json_file(subs_arr, self.json_out_filepath)
        
    
    def get_audio_out_filepath(self):
        return self.audio_file_path
    
    def get_json_out_filepath(self):
        return self.json_out_filepath
    
    def get_srt_out_filepath(self):
        return self.srt_out_filepath
