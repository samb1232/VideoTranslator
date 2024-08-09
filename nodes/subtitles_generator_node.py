from pathlib import Path

from config import AAI_API_KEY
import assemblyai as aai

from external_modules import sub_parser
from external_modules.audio_extractor import extract_audio_from_video

class VoceToSubtitlesNode:
    """Module for generating subtitles on original language"""

    def __init__(self, src_lang: str) -> None:
        aai.settings.api_key = AAI_API_KEY
        self.aai_conf = aai.TranscriptionConfig(language_code=src_lang, punctuate=True)

    def transcript(self, video_file_path: str, out_file_path: str):
        video_file_name = video_file_path.split("\\")[-1].split("/")[-1]
        temp_path = video_file_name.split(".")[-2]
        if len(temp_path) < 2:
            temp_path = video_file_name

        out_folder_path = video_file_path.replace(video_file_name, "")
        if len(out_folder_path) != 0:
            audio_file_path = f"{out_folder_path}\\audio_{temp_path}.wav"
        else:
            audio_file_path = f"audio_{temp_path}.wav"

        extract_audio_from_video(video_file_path, audio_file_path)
        
        transcript = aai.Transcriber().transcribe(video_file_path, self.aai_conf)

        # Ensure the output directory exists
        output_dir = Path(out_file_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        subtitles = transcript.export_subtitles_srt()

        subtitles = sub_parser.correct_subtitles_length(subtitles)

        with open(out_file_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(subtitles)

