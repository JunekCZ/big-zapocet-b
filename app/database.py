from pymongo import MongoClient
import redis
from .config import Config

# Nastavení MongoDB
client = MongoClient(Config.MONGO_URI)
db = client["articles"]
articles = db["articles"]
users = db["users"]

# Nastavení Redis
redis_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
