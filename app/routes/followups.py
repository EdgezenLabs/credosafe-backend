from fastapi import APIRouter, Depends
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.schemas.application_schema import ApplicationOut
from app.crud import crud

router = APIRouter()

@router.get("/", response_model=dict)
def list_followups(skip: int = 0, limit: int = 25, status: str = None, db: Session = Depends(get_db)):
    items = crud.list_followups(db, status=status, skip=skip, limit=limit)
    return {"total": len(items), "items": items}

@router.post("/", status_code=201)
def create_followup(payload: dict, db: Session = Depends(get_db)):
    rec = crud.create_followup(db, payload)
    return rec
