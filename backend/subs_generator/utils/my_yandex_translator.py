import requests


class MyYandexTranslator:
    def __init__(self, api_key, folder_id, src_lang, dest_lang):
        self.api_key = api_key
        self.folder_id = folder_id
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'

    def translate(self, text: str):
        params = {
            'folder_id': self.folder_id,
            'texts': [text],
            'sourceLanguageCode': self.src_lang,
            'targetLanguageCode': self.dest_lang,
            'format': 'PLAIN_TEXT'
        }
        headers = {
            'Authorization': f'Api-Key {self.api_key}'
        }

        response = requests.post(self.url, json=params, headers=headers)
        response_data = response.json()

        if 'translations' in response_data:
            return response_data['translations'][0]['text']
        else:
            raise Exception("Error in yandex translator")
