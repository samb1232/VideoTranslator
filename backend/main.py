from modules.subs_generator import SubsGenerator
from modules.subs_translator import SubsTranslator, Translators
from modules.subs_gpt_corrector import correct_json_gender_and_numbers
from modules.voice_generator import VoiceGenerator

src_lang = "en"
target_lang = "ru"
folder_name = "test_files\\0000"
video_file_name = "test"

genders_dict = {
    "A": False,
}

orig_subs_filepath = f"{folder_name}\\{video_file_name}_{src_lang}.json"
trans_subs_filepath = f"{folder_name}\\{video_file_name}_{target_lang}.json"
corrected_subs_filepath = f"{folder_name}\\{video_file_name}_{target_lang}_corrected.json"

voice_node = SubsGenerator(src_lang)
voice_node.transcript(f"{folder_name}\\{video_file_name}.mp4", folder_name)
print("Subs extractions done!") 

translator_node = SubsTranslator(Translators.yandex, src_lang, target_lang, " //")
translator_node.translate_json_file(orig_subs_filepath, trans_subs_filepath)
print("Translation done!")

correct_json_gender_and_numbers(
    in_json_filepath=trans_subs_filepath,
    speakers_genders_dict=genders_dict,
    out_json_filepath=corrected_subs_filepath
)
print("Subs correction done!")

sg_node = VoiceGenerator(language=target_lang)
sg_node.generate_audio(
    orig_wav_filepath=f"{folder_name}\\{video_file_name}_{src_lang}.wav",
    json_subs_filepath=corrected_subs_filepath,
    out_wav_filepath=f"{folder_name}\\{video_file_name}_{target_lang}.wav"
    )
print("Dub generation done!")


print("Finish!")
