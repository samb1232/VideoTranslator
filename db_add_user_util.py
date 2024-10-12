
from backend.database.models import User, db
from backend.web_server import app

def add_user(username, password):
    with app.app_context():
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} added successfully.")

if __name__ == '__main__':
    username = "admin"
    password = "admin"
    add_user(username, password)
