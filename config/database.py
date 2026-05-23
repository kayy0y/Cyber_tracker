from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

_db = None

def get_db():
    global _db

    if _db is None:

        mongo_uri = os.getenv('MONGO_URI')

        if not mongo_uri:
            raise Exception("❌ MONGO_URI environment variable is missing")

        try:
            client = MongoClient(mongo_uri)

            # Test connection
            client.admin.command('ping')

            # Database name
            _db = client['cyber-compliance']

            print("✅ MongoDB Connected Successfully")

        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise e

    return _db
