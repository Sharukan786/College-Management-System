from typing import Optional, Union
from pymongo import MongoClient
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path)

def check_db():
    uri = os.getenv("MONGODB_URI")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=20000)
        db = client["cms"]
        print(f"COUNT: {db.staff_detail.count_documents({})}")
        for s in db.staff_detail.find().limit(5):
            print(f"STAFF: {s.get('staffName')} | {s.get('staffId')}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_db()
