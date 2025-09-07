from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MongoConnection:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self.connect()

    def connect(self):
        try:
            mongodb_config = settings.MONGODB_SETTINGS
            self._client = MongoClient(mongodb_config['HOST'])
            self._db = self._client[mongodb_config['DB_NAME']]
            logger.info("Connected to MongoDB successfully")
            print("✅ Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            print(f"❌ MongoDB connection failed: {e}")

    def get_db(self):
        if self._db is None:
            self.connect()
        return self._db

    def get_collection(self, collection_name):
        return self.get_db()[collection_name]

# Global instance
mongo_connection = MongoConnection()

def get_mongo_db():
    return mongo_connection.get_db()

def get_collection(collection_name):
    return mongo_connection.get_collection(collection_name)
