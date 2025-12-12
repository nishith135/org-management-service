from pydantic import BaseModel, EmailStr


class OrgCreateRequest(BaseModel):
    organization_name: str
    admin_email: EmailStr
    admin_password: str


class OrgUpdateRequest(BaseModel):
    current_organization_name: str
    new_organization_name: str
    admin_email: EmailStr
    admin_password: str


class OrgDeleteRequest(BaseModel):
    organization_name: str
