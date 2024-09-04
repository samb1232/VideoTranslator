import json
import os

from config import AAI_API_KEY
import assemblyai as aai

from modules.utilities.audio_extractor import extract_audio_from_video
from modules.utilities.sub_parser import format_time_ms_to_str

class SubsGenerator:
    """Module for generating subtitles on original language"""
    MAX_PAUSE_DURATION_MS = 400
    MAX_SYMBOLS_PER_SUBTITLE = 500
    END_SENTENCE_SYMBOLS = ".?;:!"

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
        self.id_counter = 1

    def _split_utterance(self, utterance: aai.Utterance):
        """
        Splits an utterance into multiple parts if the pause between sentences exceeds MAX_PAUSE_DURATION_MS.

        :param utterance: The utterance object to split.
        :return: A list of split subtitles in dict format.
        """
        words_arr = utterance.words
        split_subtitles = []
        current_subtitle = {
            "id": self.id_counter,
            "speaker": utterance.speaker,
            "text": words_arr[0].text,
            "start": format_time_ms_to_str(words_arr[0].start),
            "end": format_time_ms_to_str(words_arr[0].end)
        }

        for i in range(1, len(words_arr)):
            pause_duration = words_arr[i].start - words_arr[i-1].end
            is_end_of_sentence = words_arr[i-1].text[-1] in self.END_SENTENCE_SYMBOLS
            if is_end_of_sentence and (pause_duration > self.MAX_PAUSE_DURATION_MS or 
                                     len(current_subtitle["text"]) > self.MAX_SYMBOLS_PER_SUBTITLE):

                # Finalize the current subtitle
                split_subtitles.append(current_subtitle)
                self.id_counter += 1
                # Start a new subtitle
                current_subtitle = {
                    "id": self.id_counter,
                    "speaker": utterance.speaker,
                    "text": words_arr[i].text,
                    "start": format_time_ms_to_str(words_arr[i].start),
                    "end": format_time_ms_to_str(words_arr[i].end)
                }
            else:
                # Continue the current utterance
                current_subtitle["text"] += " " + words_arr[i].text
                current_subtitle["end"] = format_time_ms_to_str(words_arr[i].end)

        # Add the last subtitle
        split_subtitles.append(current_subtitle)
        self.id_counter += 1

        return split_subtitles

    def transcript(self, video_file_path: str, output_dir: str | None = None):
        video_dir, video_filename = os.path.split(video_file_path)
        if output_dir is None:
            output_dir = video_dir
        os.makedirs(output_dir, exist_ok=True)
        
        out_filename = video_filename.split(".")[-2]

        audio_file_path = os.path.join(output_dir, f"{out_filename}_{self.src_lang}.wav")

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
        for utterance in transcript.utterances:
            subs_splitted_arr = self._split_utterance(utterance)
            subs_json_arr.extend(subs_splitted_arr)
        with open(json_out_filepath, 'w', encoding='utf-8') as file:
            json.dump(subs_json_arr, file, ensure_ascii=False, indent=4)

