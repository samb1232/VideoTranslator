from pydub import AudioSegment
from pydub.playback import play

import assemblyai as aai

AAI_API_KEY: str = "ec1bf2732ca54dc08044afb224c1cdcb"

BEEP_WAV_FILEPATH = "src/beep.wav"

swears_dict = {
    "ru": [
        "сука", "сучка", "сученок", "шлюха", "шлюшка",
        "хуи", "хуево", "хуиня", "хуита", "хуетень", "хуево", "хуило", "нахуй", "нахер", "хуевый", "хуевая", "хуевые", "хуевое", "нахуя", "хуя",
        "пизда", "пиздец", "пизде", "пезды",
        "ебать", "ебануть", "ебануться", "ебырь", "ебаться", "ебанул", "ебанула", "ебануло", "ебанулась", "ебнулась", "ебитесь", "ебнуть", "ебнул", "ебнула", "ебнуться", "ебнулась", "ебнулся", "въебать", "еъебал", "въебала", "въебало", "въебали", "выебать", "выебал", "выебала", "выебана", "выебан", "ебаный", "ебанный", "заебать", "заебал", "заебала", "заебало", "доебать", "доебал", "доебада", "доебало", "выебываться", "выебывается", "выебывалась", "выебывался", "доебаться", "доебался", "доебалась", "доебалось", "съебалась", "съебалось", "съебался", "долбоеб", "ебальник", "поебанный", "поебанная", "ебля", "еблями", "еблями", "еблями",
        "дрочить", "дрочил", "дрочила", "дрочило", "подрочить", "подрочил", "подрочила", "подрочило",
        "мудак", "мудила", "мудило", "мудлан", "мудланка", "мудохуй", "мудохуйка",
        "пидор", "пидорас", "пидорка", "пидорок", "пидорочка",
        "хуйня", "хуйню", "хуйнюшка", "хуйнюшки",
        "блядина", "блядка", "блядовать", "блядство",
        "залупа", "залупка", "залупочка", "залупу",
        "манда", "манди", "мандочка", "мандочки",
        "минет", "минетка", "минеточка", "минету",
        "пиздюк", "пиздюшка", "пиздюшки",
        "трахать", "трахал", "трахала", "трахало",
        "член", "члена", "членка", "членочка",
        "блядь", "ебаныи", "блять", "дебилы", "ебанутые", "ебанутыи", "ебаныи", "ебучии", "ебаны", "еб", "мудак", "ебаный", "ебанный", "падла", "блядская", "мудила", "долбоёб", "ебучая",
        "ебаная","патла",
    ],
    "en": [
        "fuck", "fucker", "fucking", "shit", "shitfuck", "shithole", "bitch",
        "whore", "asshole", "motherfucker", "dick", "cocksucker",
        "pussy", "cunt", "twat", "slut",
        "bastard", "bitchy", "bitching",
        "asshole", "assholes", "cocksucker",
    ]
}

def beep_swears_wav(in_wav_filepath: str, lang: str, out_wav_filepath: str):
    aai.settings.api_key = AAI_API_KEY
    aai_conf = aai.TranscriptionConfig(
                language_code=lang, 
                punctuate=False, 
                speaker_labels=False,
                speech_model=aai.SpeechModel.nano
                )
    
    transcript = aai.Transcriber().transcribe(in_wav_filepath, aai_conf)

    audio = AudioSegment.from_wav(in_wav_filepath)
    beep = AudioSegment.from_wav(BEEP_WAV_FILEPATH)

    for word in transcript.words:
        word_text = word.text.lower().replace("ё", "е").replace("й", "и").replace("!", "").replace(".", "").replace(",", "").replace("?", "")
        if word_text in swears_dict[lang]:
            word_middle = word.start  + (word.end - word.start) // 2

            start_time = word.start + (word_middle - word.start) // 2
            end_time = word.end - (word.end - word_middle) // 2
            beep_duration = end_time - start_time
            beep_segment = beep[:beep_duration]
            audio = audio[:start_time] + beep_segment + audio[end_time:]
    audio.export(out_wav_filepath, format="wav")



beep_swears_wav("test_files\\casino\\cas.wav","ru","test_files\\casino\\cas_censored.wav")