import json
import requests

from backend.config import YA_GPT_API_KEY, YA_GPT_FOLDER_ID
from modules.utilities.sub_parser import parse_json_to_subtitles, write_subs_arr_to_json_file

api_key = YA_GPT_API_KEY
folder_id = YA_GPT_FOLDER_ID

MAX_TEXT_LEN = 1500


def correct_text_by_gpt(text: str, is_female: bool):
    text_len = len(text)
    if text_len > MAX_TEXT_LEN:
        raise ValueError(f"Text length is  too long.  Max length is {MAX_TEXT_LEN}, but  got {text_len}")

    gender = "женщины" if is_female else "мужчины"
    prompt = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "user",
                "text": ("Не объясняй что ты делаешь. Не ссылайся на себя. Не дополняй текст."
                         "Ты профессиональный корректор текста. Тебе нужно выполнить только две задачи: "
                         f"1. Исправь текст на русском языке так, чтобы он был написан от лица {gender}. " 
                         "2. Замени все числа в тексте на эквивалентные слова на русском языке. "
                         f"Текст: \"{text}\". Напиши в ответе ТОЛЬКО исправленный текст"
                         )
            },
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = json.loads(response.text)["result"]["alternatives"][0]["message"]["text"]
    return result


def correct_subs_gender_and_numbers(subtitles_arr, speakers_genders_dict):
    """
    subtitles_arr - array  of Subtitle objects;
    speakers_genders_dict - dict where keys is speakers names and values is bool  (True - female, False - male)
    """
    new_subs = subtitles_arr.copy()
    for subtitle in new_subs:
        if subtitle.speaker not in speakers_genders_dict:
            print(f"Warning: unknown gender for speaker {subtitle.speaker}. Setting male for default.")
            speaker_gender = False
        else:
            speaker_gender = speakers_genders_dict[subtitle.speaker]

        subtitle.text = correct_text_by_gpt(subtitle.text, speaker_gender) 
    return new_subs     


def correct_json_gender_and_numbers(in_json_filepath: str, speakers_genders_dict: dict,  out_json_filepath: str):
    subs_arr = parse_json_to_subtitles(in_json_filepath)
    fixed_subs = correct_subs_gender_and_numbers(subs_arr, speakers_genders_dict)
    write_subs_arr_to_json_file(fixed_subs, out_json_filepath)