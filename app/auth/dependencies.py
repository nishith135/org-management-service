# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from typing import Dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Validates Authorization: Bearer <token> and returns decoded token payload.
    Raises 401 on failure.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # payload must include admin identification (email or admin_id) and organization_id
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
