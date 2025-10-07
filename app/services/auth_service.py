from sqlalchemy.orm import Session
from app.crud import crud
from app.core.security import create_access_token
from datetime import datetime, timedelta, timezone # <-- ADDED timezone
import random
from app.models.otp_codes import OTPCodes
from app.core.utils import send_email_otp

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def verify_otp_and_get_token(self, principal: str, code: str, purpose: str):
        ok = crud.verify_otp(self.db, principal=principal, code=code, purpose=purpose)
        if not ok:
            return None

        if "@" in principal:
            user = crud.get_user_by_email(self.db, principal)
        else:
            user = crud.get_user_by_phone(self.db, principal)

        if not user:
            from app.schemas.user_schema import UserCreate
            uc = UserCreate(
                name=principal.split("@")[0] if "@" in principal else principal,
                email=principal if "@" in principal else None,
                phone=None if "@" in principal else principal
            )
            user = crud.create_user(self.db, uc)

        token = create_access_token({
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "role": user.role
        })
        return {"access_token": token, "token_type": "bearer"}


def send_otp_service(db: Session, principal: str, purpose: str = "login", tenant_id=None):
    """Generate and send OTP to user's email or phone"""
    otp_code = str(random.randint(100000, 999999))
    
    # FIX: Use datetime.now(timezone.utc) for timezone-aware timestamp
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    otp_entry = OTPCodes(
        tenant_id=tenant_id,
        purpose=purpose,
        principal=principal,
        code=otp_code,
        expires_at=expiry_time,
        used=False,
    )
    db.add(otp_entry)
    db.commit()

    send_email_otp(recipient_email=principal, otp_code=otp_code)

    return {
        "message": f"OTP sent successfully to {principal}",
        "expires_in_minutes": 5
    }
