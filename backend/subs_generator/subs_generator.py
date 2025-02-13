import os

from config import AAI_API_KEY
import assemblyai as aai

from utils.audio_worker import extract_audio_from_video
from shared_utils.sub_parser import export_subtitles_to_json_file
from utils.subtitle_splitter import SubtitleSplitter


class SubsGenerator:
    """Module for generating subtitles in original language"""

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

        self.srt_out_filepath = os.path.join(output_dir, f"{out_filename}_src.srt")
        self._save_subtitles_to_srt(transcript, self.srt_out_filepath)
        self.json_out_filepath = os.path.join(output_dir,  f"{out_filename}_src.json")
        self._save_subtitles_to_json(transcript, self.json_out_filepath)
        
    
    def _save_subtitles_to_srt(self, transcript: aai.Transcript, srt_filepath: str):
        subtitles = transcript.export_subtitles_srt()
        with open(srt_filepath, "w", encoding="utf-8") as srt_file:
            srt_file.write(subtitles)
        
    def _save_subtitles_to_json(self, transcript: aai.Transcript, json_filepath: str):
        sub_splitter = SubtitleSplitter()
        subtitles = sub_splitter.split_utterances_to_subtitles(transcript.utterances)
        export_subtitles_to_json_file(subtitles, json_filepath)
        
        
    def get_audio_out_filepath(self):
        return self.audio_file_path
    
    
    def get_json_out_filepath(self):
        return self.json_out_filepath
    
    
    def get_srt_out_filepath(self):
        return self.srt_out_filepath
