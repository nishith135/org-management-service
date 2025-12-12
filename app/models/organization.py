from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid objectid")
            return ObjectId(v)
        raise ValueError("Invalid objectid")


class OrganizationBase(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=100)
    collection_name: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    admin_email: Optional[str] = None
    admin_password: Optional[str] = Field(None, min_length=6)


class OrganizationUpdate(BaseModel):
    current_organization_name: Optional[str] = None
    new_organization_name: Optional[str] = Field(None, min_length=1, max_length=100)
    collection_name: Optional[str] = None
    admin_email: Optional[str] = None
    admin_password: Optional[str] = Field(None, min_length=6)


class Organization(OrganizationBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    collection_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "organization_name": "Acme Corp",
                "collection_name": "org_acme_corp",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    }
