from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

_db = None

def get_db():
    global _db
    if _db is None:
        try:
            client = MongoClient(os.getenv('MONGO_URI'))
            # Ping to confirm connection works
            client.admin.command('ping')
            _db = client.get_database('cyber-compliance')
            print("✅ MongoDB Connected Successfully")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise e
    return _db
