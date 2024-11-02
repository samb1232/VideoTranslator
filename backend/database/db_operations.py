from datetime import datetime
import json
import os
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from modules.utilities.task_status_enum import TaskStatus
from database.models import Task, User, db

def get_user_by_username(username: str) -> User:
    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id: str) -> User:
    return User.query.filter_by(id=user_id).first()


def get_all_tasks_list() -> List[Task]:
    return Task.query.order_by(Task.creation_date).all()


def get_task_by_id(task_id: str) -> Task:
    return Task.query.filter_by(id=task_id).first()


def create_new_task(title: str, creator_username: str) -> Task:
    new_task = Task(
        title=title,
        creator_username=creator_username,
        last_used=datetime.now(),
        creation_date = datetime.now()
    )
    db.session.add(new_task)
    db.session.commit()
    return new_task


def delete_task_by_id(task_id: str) -> bool:
    task = get_task_by_id(task_id)
    if task is None:
        return False
    db.session.delete(task)
    db.session.commit()
    return True


def set_task_subs_generation_status(task_id: str, status: TaskStatus):
    task = get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with id {task_id} not found")
    task.subs_generation_status = status.value
    task.last_used=datetime.now()
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    
    
def set_task_voice_generation_status(task_id: str, status: TaskStatus):
    task = get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with id {task_id} not found")
    task.voice_generation_status = status.value
    task.last_used=datetime.now()
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    

def update_task_after_subs_created(
        task_id: str, 
        lang_from: str, 
        lang_to: str, 
        src_vid_path: str,
        src_audio_path: str, 
        srt_orig_subs_path: str, 
        srt_translated_subs_path: str, 
        json_translated_subs_path: str
        ):
    task = get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with id {task_id} not found")
    task.lang_from = lang_from
    task.lang_to = lang_to
    task.src_vid_path = src_vid_path
    task.src_audio_path = src_audio_path
    task.srt_orig_subs_path = srt_orig_subs_path
    task.srt_translated_subs_path = srt_translated_subs_path
    task.json_translated_subs_path = json_translated_subs_path
    task.last_used=datetime.now()
    task.subs_generation_status=TaskStatus.idle.value
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def update_task_after_voice_generated(
        task_id: str, 
        translated_audio_path: str,
        translated_video_path: str,
        ):
    task = get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Task with id {task_id} not found")
    task.translated_audio_path = translated_audio_path
    task.translated_video_path = translated_video_path
    task.last_used=datetime.now()
    task.voice_generation_status=TaskStatus.idle.value
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def reset_all_tasks_status():
    tasks = Task.query.all()
    for task in tasks:
        task.subs_generation_status = TaskStatus.idle.value
        task.voice_generation_status = TaskStatus.idle.value
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    

def add_users_from_json(json_filepath: str):
    if not os.path.exists(json_filepath): 
        return
    try:
        with open(json_filepath, 'r') as json_file:
            users_data = json.load(json_file)
    except  FileNotFoundError:
        print(f"File {json_filepath} not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return
    try:
        for user in users_data:
            if User.query.filter_by(username=user["username"]).first() is None:
                new_user = User(username=user["username"], password=user["password"])
                db.session.add(new_user)
    except KeyError as e:
        print(f"Missing key in JSON data: {e}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing to database: {e}")
        db.session.rollback()
