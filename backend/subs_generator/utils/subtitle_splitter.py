import re
from typing import List

import assemblyai as aai
from shared_utils.sub_parser import Subtitle


class SubtitleSplitter:
    MAX_PAUSE_BETWEEN_WORDS_MS = 1000
    MAX_SYMBOLS_PER_SUBTITLE = 200
    END_SENTENCE_SYMBOLS = ".?;:!"

    def __init__(self):
        self.id_counter = 1

    def split_utterances_to_subtitles(self, utterances: List[aai.Utterance]) -> List[Subtitle]:
        subtitles_arr = []

        for utterance in utterances:
            sentence_lengths = self._get_sentence_lengths_from_text(utterance.text)
            sentences_counter = 0
            words = utterance.words

            current_subtitle = self._create_subtitle(words[0], utterance.speaker)

            for i in range(1, len(words)):
                is_end_of_sentence = self._check_if_word_is_end_of_sentence(words[i-1])

                condition_pause = self._check_pause_between_words(words[i], words[i-1])
                
                condition_text_max_length = is_end_of_sentence and self._check_text_max_length(current_subtitle.text, self.MAX_SYMBOLS_PER_SUBTITLE)
                condition_next_sentence_too_big = is_end_of_sentence and (
                    sentences_counter + 1 < len(sentence_lengths)) and (
                    sentence_lengths[sentences_counter + 1] > self.MAX_SYMBOLS_PER_SUBTITLE - len(current_subtitle.text)
                )
                condition_current_sentence_too_big = self._check_text_max_length(current_subtitle.text,  2 * self.MAX_SYMBOLS_PER_SUBTITLE)
                
                if condition_pause or condition_text_max_length or condition_next_sentence_too_big or condition_current_sentence_too_big:
                    subtitles_arr.append(current_subtitle)
                    current_subtitle = self._create_subtitle(words[i], utterance.speaker)
                    sentences_counter += 1 if is_end_of_sentence else 0
                else:
                    self._update_subtitle(current_subtitle, words[i])

            subtitles_arr.append(current_subtitle)

        return subtitles_arr

    def _check_if_word_is_end_of_sentence(self, word: aai.Word):
        return word.text[-1] in self.END_SENTENCE_SYMBOLS
        
    def _check_pause_between_words(self, current_word: aai.Word, previous_word: aai.Word) -> bool:
        pause_between_words = current_word.start - previous_word.end
        return pause_between_words > self.MAX_PAUSE_BETWEEN_WORDS_MS
    
    def _check_text_max_length(self, text: str, max_length: int) -> bool:
        return len(text) > max_length
    
    def _get_sentence_lengths_from_text(self, text: str) -> List[int]:
        sentence_end_pattern = f"[{re.escape(self.END_SENTENCE_SYMBOLS)}]"
        sentences = re.split(sentence_end_pattern, text)
        sentence_lengths = [len(sentence.strip()) for sentence in sentences if sentence.strip()]
        return sentence_lengths

    def _create_subtitle(self, word: aai.Word, speaker: str) -> Subtitle:
        subtitle = Subtitle(
            id=self.id_counter,
            start_time=word.start,
            end_time=word.end,
            speaker=speaker,
            text=word.text
        )
        self.id_counter += 1
        return subtitle

    def _update_subtitle(self, subtitle: Subtitle, word: aai.Word):
        subtitle.text += " " + word.text
        subtitle.end_time = word.end
