from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth_schema import LoginSchema, TokenSchema

router = APIRouter()

@router.post("/verify-otp", response_model=TokenSchema)
def verify_otp(payload: LoginSchema, db: Session = Depends(get_db)):
    return AuthService(db).verify_otp(payload)
