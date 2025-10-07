from pydantic import BaseModel, EmailStr, Field
from typing import Optional

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
