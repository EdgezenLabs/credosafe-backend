from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    email: EmailStr
    otp: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
