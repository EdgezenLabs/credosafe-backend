from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationCreate(BaseModel):
    user_id: str
    loan_product_id: str
    amount_requested: float
    tenure: int
    tenant_id: Optional[str] = None
    agent_id: Optional[str] = None
    notes: Optional[str] = None

class ApplicationOut(BaseModel):
    id: str
    tenant_id: Optional[str]
    user_id: Optional[str]
    agent_id: Optional[str]
    loan_product_id: Optional[str]
    amount_requested: float
    tenure: int
    status: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True
