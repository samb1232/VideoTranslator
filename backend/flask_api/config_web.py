import os
import redis
import dotenv
import os


class ConfigWeb:
    dotenv.load_dotenv()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.getenv("flask_secret_key")

    SESSION_TYPE = "redis"
    redis_url = os.getenv('REDIS_URL')
    SESSION_REDIS = redis.from_url(redis_url)
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'flask_session:'

    UPLOAD_FOLDER = 'uploads'
    


  
    
