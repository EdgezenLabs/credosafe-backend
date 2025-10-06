from sqlalchemy.orm import Session
from app.crud import crud
from app.core.security import create_access_token
from datetime import timedelta

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def request_otp(self, principal: str, purpose: str, tenant_id: str = None):
        rec = crud.create_otp(self.db, principal=principal, purpose=purpose, tenant_id=tenant_id)
        # TODO: integrate with SMS/Email provider to deliver OTP
        return rec

    def verify_otp_and_get_token(self, principal: str, code: str, purpose: str):
        ok = crud.verify_otp(self.db, principal=principal, code=code, purpose=purpose)
        if not ok:
            return None
        # find user by principal or create
        user = None
        if "@" in principal:
            user = crud.get_user_by_email(self.db, principal)
        else:
            user = crud.get_user_by_phone(self.db, principal)
        if not user:
            # create customer user
            from app.schemas.user_schema import UserCreate
            uc = UserCreate(name=principal.split("@")[0] if "@" in principal else principal, email=principal if "@" in principal else None, phone=None if "@" in principal else principal)
            user = crud.create_user(self.db, uc)
        token = create_access_token({"user_id": str(user.id), "tenant_id": str(user.tenant_id) if user.tenant_id else None, "role": user.role})
        return {"access_token": token, "token_type": "bearer"}
