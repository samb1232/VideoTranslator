import json
import os

from config import AAI_API_KEY
import assemblyai as aai

from external_modules.audio_extractor import extract_audio_from_video
from external_modules.sub_parser import format_time_ms_to_str

class VoceToSubtitlesNode:
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
        elif not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        
        
        out_filename = video_filename.split(".")[-2]

        audio_file_path = os.path.join(output_dir, f"audio_{out_filename}_{self.src_lang}.wav")

        extract_audio_from_video(video_file_path, audio_file_path)
        
        transcript = aai.Transcriber().transcribe(audio_file_path, self.aai_conf)

        # Export subtitles as srt
        subtitles = transcript.export_subtitles_srt()
        srt_out_filepath = os.path.join(output_dir,  f"{out_filename}_{self.src_lang}.srt")
        # subtitles = correct_subtitles_length(subtitles)
        with open(srt_out_filepath, "w", encoding="utf-8") as srt_file:
            srt_file.write(subtitles)

        #Export subtitles as json
        json_out_filepath = os.path.join(output_dir,  f"{out_filename}_{self.src_lang}.json")
        subs_json_arr = []
        for index, utterance in enumerate(transcript.utterances):
            new_sub = {
                "id": index,
                "speaker": utterance.speaker,
                "text": utterance.text,
                "start": format_time_ms_to_str(utterance.start),
                "end": format_time_ms_to_str(utterance.end)
            }
            subs_json_arr.append(new_sub)
        with open(json_out_filepath, 'w', encoding='utf-8') as file:
            json.dump(subs_json_arr, file, ensure_ascii=False, indent=4)

