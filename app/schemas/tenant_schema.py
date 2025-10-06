# app/schemas/tenant_schema.py

from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict # Import ConfigDict for Pydantic V2


# Base Schema: Shared attributes
class TenantBase(BaseModel):
    name: str
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    theme: Dict[str, Any] = {}
    config: Dict[str, Any] = {}


# Creation Schema: Used for POST/creating a new tenant
class TenantCreate(TenantBase):
    # No 'id' or 'created_at' needed here, as the database generates them.
    # All fields from TenantBase are used.
    pass


# Update Schema: Used for PUT/PATCH/updating an existing tenant
class TenantUpdate(TenantBase):
    # All fields are optional when updating, set defaults to None or keep default
    name: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    theme: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


# Read Schema: Used for GET/returning a tenant (includes DB-generated fields)
class TenantOut(TenantBase):
    id: UUID # The DB-generated UUID
    created_at: Optional[str] = None # Assuming you want to read this as a string or datetime object

    # Pydantic V2 Config: Renamed from 'orm_mode'
    model_config = ConfigDict(from_attributes=True)