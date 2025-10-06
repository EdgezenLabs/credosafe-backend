from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.loan_schema import LoanProductCreate
from app.crud import crud

router = APIRouter()

@router.get("/", response_model=dict)
def list_products(skip: int = 0, limit: int = 25, tenant_id: str = None, db: Session = Depends(get_db)):
    items = crud.list_loan_products(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return {"total": len(items), "items": items}

@router.post("/", status_code=201)
def create_product(payload: LoanProductCreate, db: Session = Depends(get_db)):
    p = crud.create_loan_product(db, payload)
    return p

@router.get("/{id}")
def get_product(id: str, db: Session = Depends(get_db)):
    p = db.query(crud.lp_model.LoanProduct).filter(crud.lp_model.LoanProduct.id == id).first()
    if not p:
        raise HTTPException(status_code=404)
    return p
