from fastapi import APIRouter
from app.models.admin import AdminLoginRequest
from app.models.response import APIResponse
from app.services.auth_service import authenticate_admin
from app.utils.jwt import create_access_token
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login", response_model=APIResponse)
async def admin_login(payload: AdminLoginRequest):
    """
    Admin login endpoint

    - **email**: Admin email address
    - **password**: Admin password

    Returns JWT token on successful authentication
    """
    try:
        # Authenticate admin
        admin = await authenticate_admin(payload.email, payload.password)

        if not admin:
            return error_response(
                code="AUTH_FAILED",
                message="Invalid email or password",
                status_code=401
            )

        # Create JWT token
        token_data = {
            "sub": admin["id"],
            "email": admin["email"],
            "organization_id": admin.get("organization_id"),
            "type": "admin"
        }
        access_token = create_access_token(data=token_data)

        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer"
            },
            status_code=200
        )

    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message="An error occurred during login",
            details={"error": str(e)},
            status_code=500
        )
