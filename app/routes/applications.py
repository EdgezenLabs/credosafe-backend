from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.application_schema import ApplicationCreate
from app.crud import crud

router = APIRouter()

@router.get("/", response_model=dict)
def list_applications(skip: int = 0, limit: int = 25, status: str = None, user_id: str = None, agent_id: str = None, db: Session = Depends(get_db)):
    items = crud.list_applications(db, status=status, user_id=user_id, agent_id=agent_id, skip=skip, limit=limit)
    return {"total": len(items), "items": items}

@router.post("/", status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    a = crud.create_application(db, payload)
    return a

@router.get("/{id}")
def get_application(id: str, db: Session = Depends(get_db)):
    a = crud.get_application(db, id)
    if not a:
        raise HTTPException(status_code=404)
    return a

@router.patch("/{id}")
def update_application(id: str, payload: dict, db: Session = Depends(get_db)):
    status = payload.get("status")
    notes = payload.get("notes")
    updated = crud.update_application_status(db, id, status, notes)
    if not updated:
        raise HTTPException(status_code=404)
    return updated
