import pytest
import requests_mock

from speech_to_text.utils.my_yandex_translator import MyYandexTranslator

@pytest.fixture
def translator():
    api_key = 'test_api_key'
    folder_id = 'test_folder_id'
    src_lang = 'en'
    dest_lang = 'ru'
    return MyYandexTranslator(api_key, folder_id, src_lang, dest_lang)


def test_translate_success(translator):
    with requests_mock.Mocker() as m:
        mock_response = {
            'translations': [{'text': 'Привет, мир!'}]
        }
        m.post('https://translate.api.cloud.yandex.net/translate/v2/translate', json=mock_response)

        result = translator.translate('Hello, world!')
        assert result == 'Привет, мир!'


def test_translate_failure(translator):
    with requests_mock.Mocker() as m:
        mock_response = {
            'error': 'Something went wrong'
        }
        m.post('https://translate.api.cloud.yandex.net/translate/v2/translate', json=mock_response)

        with pytest.raises(Exception, match="Error in yandex translator"):
            translator.translate('Hello, world!')


def test_translate_empty_text(translator):
    with requests_mock.Mocker() as m:
        mock_response = {
            'translations': [{'text': ''}]
        }
        m.post('https://translate.api.cloud.yandex.net/translate/v2/translate', json=mock_response)

        result = translator.translate('')
        assert result == ''
