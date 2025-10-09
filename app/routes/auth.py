from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService, send_otp_service
from app.schemas.auth_schema import (
    SendOTPSchema, LoginSchema, TokenSchema, SetPasswordSchema,
    EmailPasswordLoginSchema, LoginResponseSchema, UserDetails
)
from app.core.security import get_current_user_email, create_access_token
from app.crud import crud

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


@router.post("/set-password")
def set_password(
    payload: SetPasswordSchema, 
    current_user: dict = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """Set password for user after OTP verification"""
    # Get user by ID from token
    user = crud.get_user(db, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify that the email in payload matches the user's email from token
    if current_user["email"] != payload.email:
        raise HTTPException(status_code=403, detail="Email mismatch with authenticated user")
    
    # Update user password
    updated_user = crud.update_user_password(db, payload.email, payload.password)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to update password")
    
    return {"message": "Password set successfully", "email": payload.email}


@router.post("/login", response_model=LoginResponseSchema)
def login(
    payload: EmailPasswordLoginSchema, 
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    # Authenticate user
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Invalid email or password"
        )
    
    # Create access token
    token = create_access_token({
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        "role": user.role,
        "email": user.email,
        "phone": user.phone
    })
    
    # Prepare user details
    user_details = UserDetails(
        id=str(user.id),
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        created_at=user.created_at
    )
    
    return LoginResponseSchema(
        access_token=token,
        token_type="bearer",
        user=user_details
    )
