import logging
import queue
import threading
import os
from modules.utilities.task_status_enum import TaskStatus
from modules.subs_generator import SubsGenerator
from modules.subs_translator import SubsTranslator, Translators
from modules.voice_generator import VoiceGenerator
from flask_app import app
from modules.utilities.file_utils import get_task_folder
from database import db_operations


class SubsCreatorQueueItem:
    def __init__(self, task_id, vid_filepath, lang_from, lang_to):
        self.task_id: str = task_id
        self.vid_filepath: str = vid_filepath
        self.lang_from: str = lang_from
        self.lang_to: str = lang_to


class VoiceGeneratorQueueItem:
    def __init__(self, task_id, src_audio_path, src_video_path, json_subs_path, lang_to):
        self.task_id: str = task_id
        self.src_audio_path: str = src_audio_path
        self.src_video_path: str = src_video_path
        self.json_subs_path: str = json_subs_path
        self.lang_to: str = lang_to


subs_queue = queue.Queue()
voice_queue = queue.Queue()


def subs_worker():
    logging.info("Subs worker started")
    while True:
        try:
            task: SubsCreatorQueueItem = subs_queue.get(timeout=1)
            if task is None:
                continue

            task_id = task.task_id
            vid_filepath = task.vid_filepath
            lang_from = task.lang_from
            lang_to = task.lang_to

            if not os.path.exists(vid_filepath):
                logging.warning(f"Video {vid_filepath} not exists. Skipping task")
                subs_queue.task_done()
                continue

            try:
                with app.app_context():
                    db_operations.set_task_subs_generation_status(task_id=task_id,  status=TaskStatus.processing)
                create_subs_task(task_id, vid_filepath, lang_from, lang_to)
            except Exception as e:
                logging.error("Error in subs worker: " + str(e))
            finally:
                subs_queue.task_done()
        except queue.Empty:
            continue


def voice_worker():
    logging.info("Voice worker started")
    while True:
        try:
            task: VoiceGeneratorQueueItem = voice_queue.get(timeout=1)
            if task is None:
                continue

            task_id = task.task_id
            src_audio_path = task.src_audio_path
            src_video_path = task.src_video_path
            json_subs_path = task.json_subs_path
            lang_to = task.lang_to

            try:
                with app.app_context():
                    db_operations.set_task_voice_generation_status(task_id=task_id,  status=TaskStatus.processing)
                generate_voice_task(task_id, src_audio_path, src_video_path, json_subs_path, lang_to)
                
            except Exception as e:
                logging.error("Error in voice worker: " + str(e))
            finally:
                voice_queue.task_done()
        except queue.Empty:
            continue


def start_workers():
    subs_thread = threading.Thread(target=subs_worker, daemon=True)
    voice_thread = threading.Thread(target=voice_worker, daemon=True)
    subs_thread.start()
    voice_thread.start()


def create_subs_task(task_id: str, vid_filepath: str, lang_from: str, lang_to: str):
    with app.app_context():
        task = db_operations.get_task_by_id(task_id)
    task_exists = task is not None
    files_exists = os.path.exists(vid_filepath)

    if not task_exists or not files_exists:
        return

    task_folder = get_task_folder(task_id)

    subs_generator = SubsGenerator(src_lang=lang_from)
    subs_generator.transcript(
        video_file_path=vid_filepath,
        output_dir=task_folder
        )
    json_filepath = subs_generator.get_json_out_filepath()
    srt_filepath = subs_generator.get_srt_out_filepath()
    audio_filepath = subs_generator.get_audio_out_filepath()

    subs_translator = SubsTranslator(
        translator=Translators.yandex,
        source_lang=lang_from,
        target_lang=lang_to
        )

    srt_tranlsated_filepath = os.path.join(task_folder, f"{task_id}_translated.srt")
    json_tranlsated_filepath = os.path.join(task_folder, f"{task_id}_translated.json")

    subs_translator.translate_srt_file(srt_filepath, srt_tranlsated_filepath)
    subs_translator.translate_json_file(json_filepath, json_tranlsated_filepath)

    with app.app_context():
        db_operations.update_task_after_subs_created(
            task_id=task_id,
            lang_from=lang_from,
            lang_to=lang_to,
            src_vid_path=vid_filepath,
            src_audio_path=audio_filepath,
            srt_orig_subs_path=srt_filepath,
            srt_translated_subs_path=srt_tranlsated_filepath,
            json_translated_subs_path=json_tranlsated_filepath
            )


def generate_voice_task(task_id: str, src_audio_path: str, src_video_path: str, json_subs_path: str, lang_to: str):
    with app.app_context():
        task = db_operations.get_task_by_id(task_id)
    task_exists = task is not None
    files_exists = os.path.exists(src_audio_path) and os.path.exists(json_subs_path)

    if not task_exists or not files_exists:
        return

    task_folder = get_task_folder(task_id)
    final_audio_filepath = os.path.join(task_folder, f"{task_id}_audio_{lang_to}.wav")
    final_video_filepath = os.path.join(task_folder, f"{task_id}_vid_{lang_to}.mp4")

    voice_generator = VoiceGenerator(lang_to)
    voice_generator.generate_audio(
        orig_wav_filepath=src_audio_path,
        json_subs_filepath=json_subs_path,
        out_wav_filepath=final_audio_filepath
        )
    voice_generator.replace_audio_in_video(
        in_audio_path=final_audio_filepath,
        in_video_path=src_video_path,
        out_video_path=final_video_filepath
        )
    with app.app_context():
        db_operations.update_task_after_voice_generated(
        task_id=task_id,
        translated_audio_path=final_audio_filepath,
        translated_video_path=final_video_filepath
        )
