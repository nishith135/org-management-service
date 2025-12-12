"""
Script to delete an existing organization from MongoDB
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "org_master_db")


async def delete_organization_by_collection_name(collection_name: str):
    """Delete organization by collection name"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    org_collection = db["organizations"]

    # Find the organization
    org = await org_collection.find_one({"collection_name": collection_name})

    if org:
        org_id = org["_id"]
        result = await org_collection.delete_one({"_id": org_id})
        print(
            f"Deleted organization: {org['organization_name']} (ID: {org_id})")
        print(f"   Collection name: {collection_name}")
        return True
    else:
        print(
            f"Organization with collection name '{collection_name}' not found")
        return False


async def list_all_organizations():
    """List all organizations"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    org_collection = db["organizations"]

    print("\nAll organizations:")
    count = 0
    async for org in org_collection.find():
        count += 1
        print(f"  {count}. {org['organization_name']} (ID: {str(org['_id'])})")
        print(f"     Collection: {org['collection_name']}")

    if count == 0:
        print("  No organizations found")

    return count


async def main():
    print("Checking for existing organizations...")
    await list_all_organizations()

    print("\nDeleting organization 'org_acme_corp'...")
    success = await delete_organization_by_collection_name("org_acme_corp")

    if success:
        print("\nOrganization deleted successfully!")
        print("\nRemaining organizations:")
        await list_all_organizations()
        print("\nYou can now create a new organization via the API")
    else:
        print("\nNo organization found to delete")


if __name__ == "__main__":
    asyncio.run(main())
