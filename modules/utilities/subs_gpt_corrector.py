import json
import requests

from config import YA_GPT_API_KEY, YA_GPT_FOLDER_ID

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
                "role": "system",
                "text": ("Ты профессиональный корректор переведённого текста. " 
                f"Ты должен исправить текст на русском языке так, чтобы он был написан от лица {gender}. Также замени все числа в тексте на эквивалентные слова на русском языке."
                "Не объясняй что ты делаешь. Не ссылайся на себя. Не пиши в ответе ничего, кроме исправленного текста."
                )
            },
            {
                "role": "user",
                "text": text
            }
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
