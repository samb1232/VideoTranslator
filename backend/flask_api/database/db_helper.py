from datetime import datetime
import json
import os
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from logging_conf import setup_logging
from database.db_base import db_base
from utils.task_status_enum import TaskStatus
from database.models import Task, User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


logger = setup_logging()


class DbHelper:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DbHelper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.engine = create_engine(os.getenv('DATABASE_URL'))
            self.Session = sessionmaker(bind=self.engine)
            self.Base = db_base.Base
            self.initialized = True
            self.Base.metadata.create_all(self.engine)
            logger.info("Database connected")

    def _get_session(self):
        return self.Session()


    def get_user_by_username(self, username: str) -> User:
        logger.debug(f"Getting user with username: {username}")
        session = self._get_session()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        return user

    def get_user_by_id(self, user_id: str) -> User:
        logger.debug(f"Getting user with id: {user_id}")
        session = self._get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
        finally:
            session.close()
        return user

    def get_all_tasks_list(self) -> List[Task]:
        logger.debug("Getting all tasks list")
        session = self._get_session()
        try:
            tasks = session.query(Task).order_by(Task.creation_date).all()
        finally:
            session.close()
        return tasks

    def get_task_by_id(self, task_id: str) -> Task:
        # logger.debug(f"Getting task by id {task_id}")
        session = self._get_session()
        try:
            task = session.query(Task).filter_by(id=task_id).first()
        finally:
            session.close()
        return task
    
    def _get_task_by_id(self, task_id: str, session: Session) -> Task:
        task = session.query(Task).filter_by(id=task_id).first()
        return task

    def create_new_task(self, title: str, creator_username: str) -> Task:
        logger.debug(f"Creating new task: {title}")
        session = self._get_session()
        try:
            new_task = Task(
            title=title,
            creator_username=creator_username,
            last_used=datetime.now(),
            creation_date = datetime.now()
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return new_task

    def delete_task_by_id(self, task_id: str) -> bool:
        logger.debug(f"Deleting task with id {task_id}")
        session = self._get_session()
        try:
            task = self._get_task_by_id(task_id, session)
            if task is None:
                return False
            session.delete(task)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return True

    def set_task_subs_generation_status(self, task_id: str, status: TaskStatus):
        logger.debug(f"Setting new subs_gen status {status.value} for task {task_id}")
        session = self._get_session()
        try:
            task = self._get_task_by_id(task_id, session)
            if task is None:
                raise ValueError(f"Task with id {task_id} not found")
            task.subs_generation_status = status.value
            task.last_used=datetime.now()
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def set_task_voice_generation_status(self, task_id: str, status: TaskStatus):
        logger.debug(f"Setting new voice_gen status {status.value} for task {task_id}")
        session = self._get_session()
        try:
            task = self._get_task_by_id(task_id, session)
            if task is None:
                raise ValueError(f"Task with id {task_id} not found")
            task.voice_generation_status = status.value
            task.last_used=datetime.now()
            
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def set_task_languages(self, task_id: str, lang_from: str, lang_to: str):
        logger.debug(f"Setting new languages ({lang_from} to {lang_to}) for task {task_id}")
        session = self._get_session()
        try:
            task = self._get_task_by_id(task_id, session)
            if task is None:
                raise ValueError(f"Task with id {task_id} not found")
            task.lang_from = lang_from
            task.lang_to = lang_to
            task.last_used=datetime.now()
            task.subs_generation_status=TaskStatus.IDLE.value
            
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def set_task_src_vid_path(
            self, 
            task_id: str, 
            src_vid_path: str,
            ):
        logger.debug(f"Setting new src vid path for task {task_id}")
        session = self._get_session()
        try:
            task = self._get_task_by_id(task_id, session)
            if task is None:
                raise ValueError(f"Task with id {task_id} not found")
            task.src_vid_path = src_vid_path
            
            task.last_used=datetime.now()
            task.subs_generation_status=TaskStatus.IDLE.value
            
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def update_task_after_subs_generated(
            self, 
            task_id: str, 
            src_audio_path: str, 
            srt_orig_subs_path: str, 
            srt_translated_subs_path: str, 
            json_translated_subs_path: str
            ):
        logger.debug(f"Updating task status after subs generated ({task_id})")
        session = self._get_session()
        try:
            task = self._get_task_by_id(task_id, session)
            if task is None:
                raise ValueError(f"Task with id {task_id} not found")
            task.src_audio_path = src_audio_path
            task.srt_orig_subs_path = srt_orig_subs_path
            task.srt_translated_subs_path = srt_translated_subs_path
            task.json_translated_subs_path = json_translated_subs_path
            task.last_used=datetime.now()
            task.subs_generation_status=TaskStatus.IDLE.value
            
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_task_after_voice_generated(
            self,
            task_id: str, 
            translated_audio_path: str,
            translated_video_path: str,
            ):
        logger.debug(f"Updating task status after voice generated ({task_id})")
        session = self._get_session()
        try:
            task = self._get_task_by_id(task_id, session)
            if task is None:
                raise ValueError(f"Task with id {task_id} not found")
            task.translated_audio_path = translated_audio_path
            task.translated_video_path = translated_video_path
            task.last_used=datetime.now()
            task.voice_generation_status=TaskStatus.IDLE.value
            
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def reset_all_tasks_status(self):
        logger.debug("Resetting all tasks statuses")
        session = self._get_session()
        try:
            tasks = session.query(Task).all()
            for task in tasks:
                task.subs_generation_status = TaskStatus.IDLE.value
                task.voice_generation_status = TaskStatus.IDLE.value
    
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def add_users_from_json(self, json_filepath: str):
        logger.debug(f"Adding new users to db")
        if not os.path.exists(json_filepath): 
                return
        try:
            with open(json_filepath, 'r') as json_file:
                    users_data = json.load(json_file)
            session = self._get_session()
        
            for user in users_data:
                if session.query(User).filter_by(username=user["username"]).first() is None:
                    new_user = User(username=user["username"], password=user["password"])
                    session.add(new_user)
            
            session.commit()
        except FileNotFoundError:
            print(f"File {json_filepath} not found")
            session.rollback()
            return
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            session.rollback()
            return
        except KeyError as e:
            print(f"Missing key in JSON data: {e}")
            session.rollback()
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
            return
        except Exception as e:
            print(f"Error committing to database: {e}")
            session.rollback()
        finally:
            session.close()
