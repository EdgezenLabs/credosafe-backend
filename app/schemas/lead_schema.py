# app/schemas/lead_schema.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

# --- Define Base/Common Lead Fields ---
class LeadBase(BaseModel):
    # Replace these placeholder fields with your actual column names and types
    tenant_id: UUID
    status: str = "New" 
    client_name: str
    phone_number: str
    email: Optional[str] = None
    loan_amount_requested: float
    
    # You will likely need more fields here matching your 'leads' table.


# --- Creation Schema ---
# This is the class needed to fix the AttributeError
class LeadCreate(LeadBase):
    # Inherits all fields from LeadBase. 
    # Add any fields specific to creation here, if necessary.
    pass


# --- Update Schema ---
class LeadUpdate(LeadBase):
    # Make most fields optional for updates
    tenant_id: Optional[UUID] = None
    status: Optional[str] = None
    client_name: Optional[str] = None
    phone_number: Optional[str] = None
    loan_amount_requested: Optional[float] = None


# --- Read/Response Schema (includes database-generated fields) ---
class Lead(LeadBase):
    id: int # Assuming 'id' is an auto-incrementing integer in your leads table
    created_at: Optional[str] = None 
    
    # Pydantic V2 config (resolves the user warning you are seeing)
    model_config = ConfigDict(from_attributes=True)