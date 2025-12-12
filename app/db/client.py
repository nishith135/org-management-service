from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "org_master_db")

# Global database client
client: Optional[AsyncIOMotorClient] = None
database = None
_db_initialized = False


async def init_db():
    """Initialize MongoDB connection"""
    global client, database, _db_initialized
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    _db_initialized = True
    print(f"Connected to MongoDB: {DATABASE_NAME}")


async def close_db():
    """Close MongoDB connection"""
    global client, _db_initialized
    if client is not None:
        client.close()
        _db_initialized = False
        print("MongoDB connection closed")


def get_database():
    """Get database instance"""
    if not _db_initialized:
        return None
    return database
