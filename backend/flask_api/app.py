from flask import Flask
from flask_cors import CORS
from flask_session import Session
from config import ConfigWeb
from database.db_helper import DbHelper
from routes import bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(ConfigWeb)
    app.register_blueprint(bp)
    CORS(app, supports_credentials=True)
    server_session = Session(app)

    db_operations = DbHelper()
    db_operations.add_users_from_json("users.json")

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=False)
