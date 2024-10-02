
from backend.database.models import User, db


def add_user(username, password):
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    print(f"User {username} added successfully.")

if __name__ == '__main__':
    username = "admin"
    password = "admin"
    add_user(username, password)
