from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.tenant_schema import TenantCreate, TenantOut
from app.crud import crud

router = APIRouter()

@router.get("/", response_model=dict)
def list_tenants(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    items = crud.list_tenants(db, skip=skip, limit=limit)
    return {"total": len(items), "items": items}

@router.post("/", response_model=TenantOut, status_code=201)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    t = crud.create_tenant(db, payload)
    return t

@router.get("/{tenant_id}", response_model=TenantOut)
def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    t = crud.get_tenant(db, tenant_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return t
