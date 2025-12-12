import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()


async def create_admin():
    client = AsyncIOMotorClient(
        os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client[os.getenv("MONGO_DB_NAME", "org_master_db")]
    admin_collection = db["admins"]
    org_collection = db["organizations"]

    # Delete existing admin
    await admin_collection.delete_many({"email": "admin@acme.com"})
    print("Deleted existing admin")

    # Get org
    org = await org_collection.find_one({"organization_name": "Acme Global"})
    if not org:
        org = await org_collection.find_one({"organization_name": "Acme Corp"})

    if org:
        # Create hash using bcrypt directly
        password = "StrongPass123!".encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        admin_doc = {
            "email": "admin@acme.com",
            "organization_id": str(org["_id"]),
            "hashed_password": hashed,
            "is_active": True
        }
        await admin_collection.insert_one(admin_doc)
        print(f"Created admin for org: {org['organization_name']}")
        print("Password hash created successfully")
    else:
        print("No organization found")

asyncio.run(create_admin())
