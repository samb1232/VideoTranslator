from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    id = db.Column(db.String(32), unique=True, primary_key=True, default=get_uuid)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(30))

    def __repr__(self):
        return f'<User {self.username}>'
