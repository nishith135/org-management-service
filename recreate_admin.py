import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def recreate_admin():
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
        # Create new admin with proper hash
        password = "StrongPass123!"
        # Ensure password is within bcrypt limit
        if len(password.encode('utf-8')) > 72:
            password = password[:72]

        admin_doc = {
            "email": "admin@acme.com",
            "organization_id": str(org["_id"]),
            "hashed_password": pwd_context.hash(password),
            "is_active": True
        }
        await admin_collection.insert_one(admin_doc)
        print(f"Created admin for org: {org['organization_name']}")
    else:
        print("No organization found")

asyncio.run(recreate_admin())
