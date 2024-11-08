from flask_pymongo import PyMongo
import redis
from .config import Config

# Nastavení MongoDB
mongo = PyMongo(uri=Config.MONGO_URI)

# Nastavení Redis
redis_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
