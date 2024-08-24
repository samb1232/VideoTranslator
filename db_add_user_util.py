from app import create_app, db
from app.models import User

def add_user(username, password):
    app = create_app()
    with app.app_context():
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} added successfully.")

if __name__ == '__main__':
    username = "admin"
    password = "admin"
    add_user(username, password)
