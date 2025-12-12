import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def fix_password():
    client = AsyncIOMotorClient(
        os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client[os.getenv("MONGO_DB_NAME", "org_master_db")]
    admin_collection = db["admins"]

    admin = await admin_collection.find_one({"email": "admin@acme.com"})
    if admin:
        # Hash password properly
        hashed = pwd_context.hash("StrongPass123!")
        await admin_collection.update_one(
            {"email": "admin@acme.com"},
            {"$set": {"hashed_password": hashed}}
        )
        print("Password updated successfully")
    else:
        print("Admin not found - creating new admin")
        # Get org ID
        org_collection = db["organizations"]
        org = await org_collection.find_one({"organization_name": "Acme Global"})
        if org:
            admin_doc = {
                "email": "admin@acme.com",
                "organization_id": str(org["_id"]),
                "hashed_password": pwd_context.hash("StrongPass123!"),
                "is_active": True
            }
            await admin_collection.insert_one(admin_doc)
            print("Admin created successfully")

asyncio.run(fix_password())
