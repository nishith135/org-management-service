from typing import Optional, List
from datetime import datetime
from app.db.client import get_database
from app.models.organization import Organization, OrganizationCreate, OrganizationUpdate
from app.services.auth_service import get_password_hash
from bson import ObjectId
import re


def slugify(text: str) -> str:
    """Convert text to slug format"""
    # Convert to lowercase and replace spaces/special chars with underscores
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '_', slug)
    return f"org_{slug}"


async def create_organization(org_data: OrganizationCreate) -> dict:
    """
    Create a new organization

    Args:
        org_data: Organization creation data

    Returns:
        Created organization document
    """
    db = get_database()
    if db is None:
        raise Exception("Database not initialized")

    org_collection = db["organizations"]

    # Generate collection name if not provided
    collection_name = org_data.collection_name
    if not collection_name:
        collection_name = slugify(org_data.organization_name)

    # Check if collection name already exists
    existing = await org_collection.find_one({"collection_name": collection_name})
    if existing is not None:
        raise ValueError(
            f"Organization with collection name '{collection_name}' already exists")

    # Create organization document
    org_doc = {
        "organization_name": org_data.organization_name,
        "collection_name": collection_name,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = await org_collection.insert_one(org_doc)
    org_doc["id"] = str(result.inserted_id)
    org_id = str(result.inserted_id)

    # Create admin account if admin_email and admin_password are provided
    if org_data.admin_email and org_data.admin_password:
        admin_collection = db["admins"]
        admin_doc = {
            "email": org_data.admin_email,
            "organization_id": org_id,
            "hashed_password": get_password_hash(org_data.admin_password),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await admin_collection.insert_one(admin_doc)

    # Remove _id and convert datetime objects to ISO format strings for JSON serialization
    org_doc.pop("_id", None)
    if "created_at" in org_doc and isinstance(org_doc["created_at"], datetime):
        org_doc["created_at"] = org_doc["created_at"].isoformat()
    if "updated_at" in org_doc and isinstance(org_doc["updated_at"], datetime):
        org_doc["updated_at"] = org_doc["updated_at"].isoformat()

    return org_doc


async def get_organization(org_id: str) -> Optional[dict]:
    """
    Get organization by ID

    Args:
        org_id: Organization ID

    Returns:
        Organization document or None
    """
    db = get_database()
    if db is None:
        return None

    org_collection = db["organizations"]

    try:
        org_doc = await org_collection.find_one({"_id": ObjectId(org_id)})
        if org_doc:
            org_doc["id"] = str(org_doc["_id"])
            # Remove _id and convert datetime objects to ISO format strings
            org_doc.pop("_id", None)
            if "created_at" in org_doc and isinstance(org_doc["created_at"], datetime):
                org_doc["created_at"] = org_doc["created_at"].isoformat()
            if "updated_at" in org_doc and isinstance(org_doc["updated_at"], datetime):
                org_doc["updated_at"] = org_doc["updated_at"].isoformat()
        return org_doc
    except Exception:
        return None


async def get_organization_by_name(organization_name: str) -> Optional[dict]:
    """
    Get organization by name
    
    Args:
        organization_name: Organization name
    
    Returns:
        Organization document or None
    """
    db = get_database()
    if db is None:
        return None
    
    org_collection = db["organizations"]
    
    try:
        org_doc = await org_collection.find_one({"organization_name": organization_name})
        if org_doc:
            org_doc["id"] = str(org_doc["_id"])
            # Remove _id and convert datetime objects to ISO format strings
            org_doc.pop("_id", None)
            if "created_at" in org_doc and isinstance(org_doc["created_at"], datetime):
                org_doc["created_at"] = org_doc["created_at"].isoformat()
            if "updated_at" in org_doc and isinstance(org_doc["updated_at"], datetime):
                org_doc["updated_at"] = org_doc["updated_at"].isoformat()
        return org_doc
    except Exception:
        return None


async def get_all_organizations() -> List[dict]:
    """
    Get all organizations

    Returns:
        List of organization documents
    """
    db = get_database()
    if db is None:
        return []

    org_collection = db["organizations"]
    orgs = []

    async for org_doc in org_collection.find():
        org_doc["id"] = str(org_doc["_id"])
        # Remove _id and convert datetime objects to ISO format strings
        org_doc.pop("_id", None)
        if "created_at" in org_doc and isinstance(org_doc["created_at"], datetime):
            org_doc["created_at"] = org_doc["created_at"].isoformat()
        if "updated_at" in org_doc and isinstance(org_doc["updated_at"], datetime):
            org_doc["updated_at"] = org_doc["updated_at"].isoformat()
        orgs.append(org_doc)

    return orgs


async def update_organization(org_id: str, org_data: OrganizationUpdate) -> Optional[dict]:
    """
    Update an organization

    Args:
        org_id: Organization ID
        org_data: Organization update data

    Returns:
        Updated organization document or None
    """
    db = get_database()
    if db is None:
        return None

    org_collection = db["organizations"]

    # Build update document
    update_doc = {"updated_at": datetime.utcnow()}

    if org_data.organization_name is not None:
        update_doc["organization_name"] = org_data.organization_name

    if org_data.collection_name is not None:
        # Check if new collection name already exists
        existing = await org_collection.find_one({
            "collection_name": org_data.collection_name,
            "_id": {"$ne": org_id}
        })
        if existing is not None:
            raise ValueError(
                f"Organization with collection name '{org_data.collection_name}' already exists")
        
        update_doc["collection_name"] = org_data.collection_name
    
    try:
        result = await org_collection.find_one_and_update(
            {"_id": org_id},
            {"$set": update_doc},
            return_document=True
        )

        if result is not None:
            result["id"] = str(result["_id"])
            # Remove _id and convert datetime objects to ISO format strings
            result.pop("_id", None)
            if "created_at" in result and isinstance(result["created_at"], datetime):
                result["created_at"] = result["created_at"].isoformat()
            if "updated_at" in result and isinstance(result["updated_at"], datetime):
                result["updated_at"] = result["updated_at"].isoformat()

        return result
    except Exception:
        return None


async def delete_organization(org_id: str) -> bool:
    """
    Delete an organization
    
    Args:
        org_id: Organization ID
    
    Returns:
        True if deleted, False otherwise
    """
    db = get_database()
    if db is None:
        return False
    
    org_collection = db["organizations"]
    
    try:
        result = await org_collection.delete_one({"_id": ObjectId(org_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def update_organization_by_name(current_name: str, org_data: OrganizationUpdate) -> Optional[dict]:
    """
    Update an organization by name
    
    Args:
        current_name: Current organization name
        org_data: Organization update data
    
    Returns:
        Updated organization document or None
    """
    db = get_database()
    if db is None:
        return None
    
    org_collection = db["organizations"]
    
    # Find organization by current name
    existing_org = await org_collection.find_one({"organization_name": current_name})
    if not existing_org:
        return None
    
    org_id = existing_org["_id"]
    
    # Build update document
    update_doc = {"updated_at": datetime.utcnow()}
    
    if org_data.new_organization_name is not None:
        update_doc["organization_name"] = org_data.new_organization_name
        # Update collection name if organization name changes
        if not org_data.collection_name:
            update_doc["collection_name"] = slugify(org_data.new_organization_name)
    
    if org_data.collection_name is not None:
        # Check if new collection name already exists
        existing = await org_collection.find_one({
            "collection_name": org_data.collection_name,
            "_id": {"$ne": org_id}
        })
        if existing is not None:
            raise ValueError(
                f"Organization with collection name '{org_data.collection_name}' already exists")
        update_doc["collection_name"] = org_data.collection_name
    
    try:
        result = await org_collection.find_one_and_update(
            {"_id": org_id},
            {"$set": update_doc},
            return_document=True
        )
        
        if result is not None:
            result["id"] = str(result["_id"])
            # Remove _id and convert datetime objects to ISO format strings
            result.pop("_id", None)
            if "created_at" in result and isinstance(result["created_at"], datetime):
                result["created_at"] = result["created_at"].isoformat()
            if "updated_at" in result and isinstance(result["updated_at"], datetime):
                result["updated_at"] = result["updated_at"].isoformat()
        
        return result
    except Exception:
        return None


async def delete_organization_by_name(organization_name: str) -> bool:
    """
    Delete an organization by name
    
    Args:
        organization_name: Organization name
    
    Returns:
        True if deleted, False otherwise
    """
    db = get_database()
    if db is None:
        return False
    
    org_collection = db["organizations"]
    
    try:
        org_doc = await org_collection.find_one({"organization_name": organization_name})
        if not org_doc:
            return False
        result = await org_collection.delete_one({"_id": org_doc["_id"]})
        return result.deleted_count > 0
    except Exception:
        return False


async def migrate_collection(old_collection_name: str, new_collection_name: str) -> bool:
    """
    Migrate data from old collection to new collection

    Args:
        old_collection_name: Old collection name
        new_collection_name: New collection name

    Returns:
        True if migration successful, False otherwise
    """
    db = get_database()
    if db is None:
        return False

    try:
        # Check if collections exist
        collections = await db.list_collection_names()

        if old_collection_name not in collections:
            return False

        # Copy all documents from old to new collection
        old_collection = db[old_collection_name]
        new_collection = db[new_collection_name]

        async for doc in old_collection.find():
            await new_collection.insert_one(doc)

        return True
    except Exception:
        return False
