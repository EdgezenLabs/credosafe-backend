from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService, send_otp_service
from app.schemas.auth_schema import SendOTPSchema, LoginSchema, TokenSchema

router = APIRouter()

@router.post("/send-otp")
def send_otp(payload: SendOTPSchema, db: Session = Depends(get_db)):
    """Send OTP to user's email or phone"""
    if not payload.email and not payload.phone:
        raise HTTPException(status_code=400, detail="Either email or phone is required")

    principal = payload.email or payload.phone
    result = send_otp_service(db, principal=principal, purpose="login")
    return result


@router.post("/verify-otp", response_model=TokenSchema)
def verify_otp(payload: LoginSchema, db: Session = Depends(get_db)):
    """Verify OTP and return JWT"""
    principal = payload.email or payload.phone
    token = AuthService(db).verify_otp_and_get_token(
        principal=principal,
        code=payload.otp_code,
        purpose="login"
    )
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return token
