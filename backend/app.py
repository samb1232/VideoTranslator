import logging
from flask_cors import CORS
from flask_session import Session
from config import ConfigWeb
from database import db_operations
from database.models import db
from routes import register_routes
from workers import start_workers
from flask_app import app

app.config.from_object(ConfigWeb)

logging.basicConfig(
    level=app.config['LOGGING_LEVEL'],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(app.config['LOGGING_FILE']),
        logging.StreamHandler()
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

CORS(app, supports_credentials=True)

server_session = Session(app)

db.init_app(app)
with app.app_context():
    db.create_all()
    db_operations.reset_all_task_processing()
    db_operations.add_users_from_json("users.json")

register_routes(app)

start_workers()

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=False)
