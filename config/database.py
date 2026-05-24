from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

_db = None

def get_db():

    global _db

    if _db is None:

        mongo_uri = os.getenv("MONGO_URI")

        print("MONGO URI:", mongo_uri)

        if not mongo_uri:
            raise Exception("MONGO_URI missing")

        client = MongoClient(mongo_uri)

        client.admin.command("ping")

        _db = client["cyber-compliance"]

        print("✅ MongoDB Connected")

    return _db
