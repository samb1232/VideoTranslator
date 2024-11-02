from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy

from modules.utilities.task_status_enum import TaskStatus

db = SQLAlchemy()

def get_uuid() -> str:
    return uuid4().hex

class User(db.Model):
    id = db.Column(db.String(32), unique=True, primary_key=True, default=get_uuid)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(30))

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    id = db.Column(db.String(32), unique=True, primary_key=True, default=get_uuid)
    number_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    last_used = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    lang_from = db.Column(db.String(3), default='', nullable=False)
    lang_to = db.Column(db.String(3), default='', nullable=False)
    src_vid_path = db.Column(db.Text, default='', nullable=False)
    src_audio_path = db.Column(db.Text, default='', nullable=False)
    srt_orig_subs_path = db.Column(db.Text, default='', nullable=False)
    srt_translated_subs_path = db.Column(db.Text, default='', nullable=False)
    json_translated_subs_path = db.Column(db.Text, default='', nullable=False)
    translated_audio_path = db.Column(db.Text, default='', nullable=False)
    translated_video_path = db.Column(db.Text, default='', nullable=False)
    subs_generation_status = db.Column(db.Text, default=TaskStatus.idle.value, nullable=False)
    voice_generation_status = db.Column(db.Text, default=TaskStatus.idle.value, nullable=False)

    creator_username = db.Column(db.Text, default='', nullable=False)
    yt_channel = db.Column(db.Text, default='', nullable=False)
    yt_name = db.Column(db.Text, default='', nullable=False)
    yt_orig_url = db.Column(db.Text, default='', nullable=False)
    yt_our_url = db.Column(db.Text, default='', nullable=False)


    def to_json(self) -> dict:
        return {
            'id': self.id,
            'number_id': self.number_id,
            'title': self.title,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'lang_from': self.lang_from,
            'lang_to': self.lang_to,
            'src_vid_path': self.src_vid_path,
            'src_audio_path': self.src_audio_path,
            'srt_orig_subs_path': self.srt_orig_subs_path,
            'srt_translated_subs_path': self.srt_translated_subs_path,
            'json_translated_subs_path': self.json_translated_subs_path,
            'translated_audio_path': self.translated_audio_path,
            'translated_video_path': self.translated_video_path,
            'subs_generation_status': self.subs_generation_status,
            'voice_generation_status': self.voice_generation_status,
            'creator_username': self.creator_username,
            'yt_channel': self.yt_channel,
            'yt_name': self.yt_name,
            'yt_orig_url': self.yt_orig_url,
            'yt_our_url': self.yt_our_url,
        }

    
