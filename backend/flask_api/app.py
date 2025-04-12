from flask import Flask
from flask_cors import CORS
from flask_session import Session
from rabbitmq_workers import RabbitMQConsumer, RabbitMQProducer
from config_web import ConfigWeb
from database.db_helper import DbHelper
from routes import create_blueprint


def create_app():
    db_helper = DbHelper()
    db_helper.add_users_from_json("users.json")
    
    rabbitmq_consumer = RabbitMQConsumer()
    rabbitmq_client = RabbitMQProducer()
    
    app = Flask(__name__)
    app.config.from_object(ConfigWeb)
    bp = create_blueprint(db_helper, rabbitmq_consumer, rabbitmq_client)
    app.register_blueprint(bp)
    CORS(app, supports_credentials=True)
    Session(app) # add server sided session

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5050, host="0.0.0.0", debug=False)
