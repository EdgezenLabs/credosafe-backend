from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserOut
from app.services.user_service import UserService
from pydantic import BaseModel, EmailStr
import bcrypt
from app.core.security import get_current_user_email

router = APIRouter()

class AdminRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

@router.get("/", response_model=dict)
def list_users(skip: int = 0, limit: int = 25, role: str = None, db: Session = Depends(get_db)):
    s = UserService(db)
    items = s.list(skip=skip, limit=limit, role=role)
    return {"total": len(items), "items": items}

@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    s = UserService(db)
    user = s.create(payload)
    return user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    from app.crud import crud
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register-admin")
def register_admin(
    req: AdminRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new admin account (open to anyone)"""
    # Check if user already exists
    from app.crud import crud
    existing = crud.get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Hash password
    password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Create user
    from app.models.user import User
    new_user = User(
        name=req.name,
        email=req.email,
        password_hash=password_hash,
        role="admin",
        is_active=True,
        is_verified=True,
        meta={}
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "user_id": str(new_user.id), "email": new_user.email, "role": new_user.role}
