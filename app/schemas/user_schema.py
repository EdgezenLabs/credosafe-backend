from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = "customer"
    meta: Optional[Dict] = {}

class UserCreate(UserBase):
    password: Optional[str] = None
    tenant_id: Optional[str] = None

class UserOut(UserBase):
    id: str
    tenant_id: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    class Config:
        from_attributes = True
