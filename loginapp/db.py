from pymongo import MongoClient
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
mongo_client = MongoClient(os.getenv("MONGO_URI"))
mongo_db = mongo_client["myapp"]
user_collection = mongo_db["users"]

# Redis setup
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)
