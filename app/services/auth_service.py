from typing import Optional
from passlib.context import CryptContext
import bcrypt
from app.db.client import get_database
from app.models.admin import Admin
from bson import ObjectId

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        # Use bcrypt directly to avoid passlib bug detection issues
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        # Fallback to passlib if bcrypt fails
        try:
            if len(plain_password.encode('utf-8')) > 72:
                plain_password = plain_password[:72]
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Use bcrypt directly to avoid passlib bug detection issues
    try:
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')
    except Exception:
        # Fallback to passlib if bcrypt fails
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)


async def authenticate_admin(email: str, password: str) -> Optional[dict]:
    """
    Authenticate an admin user

    Args:
        email: Admin email
        password: Plain text password

    Returns:
        Admin document if authentication successful, None otherwise
    """
    db = get_database()
    if db is None:
        return None

    admin_collection = db["admins"]
    admin_doc = await admin_collection.find_one({"email": email})

    if not admin_doc:
        return None

    if not admin_doc.get("is_active", True):
        return None

    if not verify_password(password, admin_doc["hashed_password"]):
        return None

    # Convert ObjectId to string for JSON serialization
    admin_doc["id"] = str(admin_doc["_id"])
    if admin_doc.get("organization_id"):
        admin_doc["organization_id"] = str(admin_doc["organization_id"])

    return admin_doc


async def get_admin_by_id(admin_id: str) -> Optional[dict]:
    """Get admin by ID"""
    db = get_database()
    if db is None:
        return None

    admin_collection = db["admins"]
    admin_doc = await admin_collection.find_one({"_id": ObjectId(admin_id)})

    if admin_doc:
        admin_doc["id"] = str(admin_doc["_id"])
        if admin_doc.get("organization_id"):
            admin_doc["organization_id"] = str(admin_doc["organization_id"])

    return admin_doc
