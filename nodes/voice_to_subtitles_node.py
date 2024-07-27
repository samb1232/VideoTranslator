from pathlib import Path

from config import AAI_API_KEY
import assemblyai as aai


class VoceToSubtitlesNode:
    """Module for generating subtitles on original language"""

    def __init__(self, src_lang: str) -> None:
        aai.settings.api_key = AAI_API_KEY
        self.aai_conf = aai.TranscriptionConfig(language_code=src_lang, punctuate=True)

    def transcript(self, audio_file_path: str, out_file_path: str):
        transcript = aai.Transcriber().transcribe(audio_file_path, self.aai_conf)

        # Ensure the output directory exists
        output_dir = Path(out_file_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        subtitles = transcript.export_subtitles_srt()
        with open(out_file_path, "w") as srt_file:
            srt_file.write(subtitles)

