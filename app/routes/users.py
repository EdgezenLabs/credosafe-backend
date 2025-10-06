from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserOut
from app.services.user_service import UserService

router = APIRouter()

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
