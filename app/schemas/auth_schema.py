from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re
from datetime import datetime

class SendOTPSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class LoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    otp_code: str = Field(alias="otp") 

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SetPasswordSchema(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8, 
        max_length=72,  # bcrypt limitation
        description="Password must be 8-72 characters long and contain at least one uppercase, one lowercase, one digit, and one special character"
    )
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 72:
            raise ValueError('Password cannot be longer than 72 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one Number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        return v

class EmailPasswordLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserDetails(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    tenant_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserDetails
