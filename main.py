from modules.subs_generator import SubsGenerator
from modules.subs_translator import SubsTranslator, Translators
from modules.voice_generator import VoiceGenerator

src_lang = "en"
target_lang = "ru"
folder_name = "test_files\\0000"
video_file_name = "test"

orig_subs_filename = f"{folder_name}\\{video_file_name}_{src_lang}.json"
trans_subs_filename = f"{folder_name}\\{video_file_name}_{target_lang}.json"

voice_node = SubsGenerator(src_lang)
voice_node.transcript(f"{folder_name}\\{video_file_name}.mp4", folder_name)
print("Subs extractions done!")

translator_node = SubsTranslator(Translators.yandex, src_lang, target_lang, " //")
translator_node.translate_json_file(orig_subs_filename, trans_subs_filename)
print("Translation done!")

sg_node = VoiceGenerator(language=target_lang)
sg_node.generate_audio(
    orig_wav_filepath=f"{folder_name}\\{video_file_name}_{src_lang}.wav",
    json_subs_filepath=trans_subs_filename,
    out_wav_filepath=f"{folder_name}\\{video_file_name}_{target_lang}.wav"
    )
print("Dub generation done!")


print("Finish!")
