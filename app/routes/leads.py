from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.lead_schema import LeadCreate
from app.crud import crud

router = APIRouter()

@router.get("/", response_model=dict)
def list_leads(skip: int = 0, limit: int = 25, agent_id: str = None, db: Session = Depends(get_db)):
    items = crud.list_leads(db, agent_id=agent_id, skip=skip, limit=limit)
    return {"total": len(items), "items": items}

@router.post("/", status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    l = crud.create_lead(db, payload)
    return l

@router.get("/{id}")
def get_lead(id: str, db: Session = Depends(get_db)):
    l = db.query(crud.lead_model.Lead).filter(crud.lead_model.Lead.id == id).first()
    if not l:
        raise HTTPException(status_code=404)
    return l
