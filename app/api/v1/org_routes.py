from fastapi import APIRouter, Depends, Query
from uuid import uuid4
from app.models.org import OrgCreateRequest, OrgUpdateRequest, OrgDeleteRequest
from app.models.response import APIResponse
from app.services.org_service import (
    create_organization,
    get_organization_by_name,
    update_organization_by_name,
    delete_organization_by_name,
)
from app.utils.responses import success_response, error_response
from app.db.client import get_database
from app.auth.dependencies import get_current_admin

router = APIRouter(prefix="/org", tags=["organization"])


@router.post("/create", response_model=APIResponse)
async def create_org(payload: OrgCreateRequest):
    """
    Create a new organization

    - **organization_name**: Name of the organization
    - **admin_email**: Admin email address
    - **admin_password**: Admin password

    Returns created organization data
    """
    trace_id = str(uuid4())
    master_db = get_database()

    try:
        # Convert OrgCreateRequest to OrganizationCreate format for service
        from app.models.organization import OrganizationCreate
        org_data = OrganizationCreate(
            organization_name=payload.organization_name,
            admin_email=payload.admin_email,
            admin_password=payload.admin_password
        )
        org = await create_organization(org_data)
        return success_response(
            data=org,
            trace_id=trace_id,
            status_code=201
        )
    except ValueError as e:
        return error_response(
            code="ORG_CREATE_FAILED",
            message=str(e),
            details=None,
            trace_id=trace_id,
            status_code=400
        )
    except Exception as e:
        return error_response(
            code="ORG_CREATE_FAILED",
            message=str(e),
            details=None,
            trace_id=trace_id,
            status_code=500
        )


@router.get("/get", response_model=APIResponse)
async def get_org(organization_name: str = Query(..., description="Organization name")):
    """
    Get organization by name (public endpoint, no authentication required)

    - **organization_name**: Organization name

    Returns organization data
    """
    trace_id = str(uuid4())
    try:
        org = await get_organization_by_name(organization_name)
        if not org:
            return error_response(
                code="NOT_FOUND",
                message=f"Organization '{organization_name}' not found",
                trace_id=trace_id,
                status_code=404
            )
        return success_response(data=org, trace_id=trace_id)

    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message="Failed to retrieve organization",
            details={"error": str(e)},
            trace_id=trace_id,
            status_code=500
        )


@router.put("/update", response_model=APIResponse)
async def update_org(payload: OrgUpdateRequest):
    """
    Update an organization

    - **current_organization_name**: Current organization name
    - **new_organization_name**: New organization name
    - **admin_email**: Admin email for authentication
    - **admin_password**: Admin password for authentication

    Returns updated organization data
    """
    trace_id = str(uuid4())
    try:
        # Check if organization exists
        existing_org = await get_organization_by_name(payload.current_organization_name)
        if not existing_org:
            return error_response(
                code="NOT_FOUND",
                message=f"Organization '{payload.current_organization_name}' not found",
                trace_id=trace_id,
                status_code=404
            )

        # Convert OrgUpdateRequest to OrganizationUpdate format for service
        from app.models.organization import OrganizationUpdate
        org_data = OrganizationUpdate(
            current_organization_name=payload.current_organization_name,
            new_organization_name=payload.new_organization_name,
            admin_email=payload.admin_email,
            admin_password=payload.admin_password
        )

        # Update organization
        updated_org = await update_organization_by_name(
            payload.current_organization_name,
            org_data
        )

        if not updated_org:
            return error_response(
                code="UPDATE_FAILED",
                message="Failed to update organization",
                trace_id=trace_id,
                status_code=500
            )

        return success_response(data=updated_org, trace_id=trace_id)

    except ValueError as e:
        return error_response(
            code="VALIDATION_ERROR",
            message=str(e),
            trace_id=trace_id,
            status_code=400
        )
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message="Failed to update organization",
            details={"error": str(e)},
            trace_id=trace_id,
            status_code=500
        )


@router.delete("/delete", response_model=APIResponse)
async def delete_org(
    organization_name: str = Query(...,
                                   description="Organization name to delete"),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Deletes organization identified by query param `organization_name`.
    Requires OAuth2 bearer token authentication.
    """
    trace_id = str(uuid4())
    master_db = get_database()

    try:
        admin_email = current_admin.get("email") or current_admin.get(
            "sub") or current_admin.get("admin_id")
        # The service function doesn't require admin_email, but we extract it for logging/audit
        deleted = await delete_organization_by_name(organization_name)
        return success_response(data={"deleted": deleted}, trace_id=trace_id)
    except Exception as e:
        return error_response(
            code="ORG_DELETE_FAILED",
            message=str(e),
            details=None,
            trace_id=trace_id,
        )
