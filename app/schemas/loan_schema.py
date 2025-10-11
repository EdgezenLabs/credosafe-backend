from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LoanProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    interest_rate: Optional[float] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    tenure_months: Optional[List[int]] = None
    active: Optional[bool] = True

class LoanProductCreate(LoanProductBase):
    tenant_id: Optional[str] = None

class LoanProductOut(LoanProductBase):
    id: str
    tenant_id: Optional[str]
    created_at: Optional[datetime]
    class Config:
        from_attributes = True
