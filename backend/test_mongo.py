import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Path to the .env file in the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

async def test_connection():
    uri = os.getenv("MONGODB_URI")
    print(f"Testing connection to: {uri}")
    client = motor.motor_asyncio.AsyncIOMotorClient(uri, serverSelectionTimeoutMS=15000)
    try:
        await client.admin.command('ping')
        print("SUCCESS: MongoDB is reachable")
        db = client.get_database()
        print(f"Database name: {db.name}")
        
        # Check for staff data
        staff_count = await db.staff_detail.count_documents({})
        print(f"Number of staff in 'staff_detail': {staff_count}")
        
        payroll_count = await db.payroll.count_documents({})
        print(f"Number of records in 'payroll': {payroll_count}")
        
        return True
    except Exception as e:
        print(f"FAIL: Could not connect to MongoDB. {e}")
        return False

if __name__ == "__main__":
    import motor.motor_asyncio
    asyncio.run(test_connection())
