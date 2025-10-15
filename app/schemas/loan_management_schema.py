from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime, date
from decimal import Decimal

# User Loan Status Response Schemas
class LoanDetails(BaseModel):
    loan_id: str
    loan_type: Literal["Personal Loan", "Business Loan", "Home Loan", "Car Loan"]
    principal_amount: Decimal
    outstanding_balance: Decimal
    monthly_emi: Decimal
    next_due_date: date
    interest_rate: Decimal
    tenure_months: int
    tenure_remaining: int
    status: Literal["active", "overdue", "completed"]
    
    class Config:
        from_attributes = True

class DocumentStatus(BaseModel):
    document_type: str  # Allow any document type (aadhar, aadhaar, pan, income_proof, etc.)
    status: str  # Allow any status (uploaded, pending, verified, rejected, etc.)
    
    class Config:
        from_attributes = True

class DocumentDetail(BaseModel):
    document_id: str
    document_type: str  # Allow any document type
    file_name: str
    file_path: str
    status: str  # Allow any status
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class PendingApplication(BaseModel):
    application_id: str
    loan_type: Literal["Personal Loan", "Business Loan", "Home Loan", "Car Loan"]
    requested_amount: Decimal
    application_date: date
    current_step: int
    progress_steps: List[str] = ["Applied", "Documents", "Verification", "Approval"]
    status: Literal["under_review", "documents_pending", "approved", "rejected"]
    documents_required: List[DocumentStatus] = []
    documents: List[DocumentDetail] = []  # Add actual uploaded documents
    
    class Config:
        from_attributes = True

class UserLoanStatusData(BaseModel):
    user_status: Literal["has_loan", "pending_application", "new_user"]
    loan_details: Optional[LoanDetails] = None
    pending_application: Optional[PendingApplication] = None
    pending_applications: Optional[List[PendingApplication]] = None  # Support multiple applications

class UserLoanStatusResponse(BaseModel):
    status: str = "success"
    data: UserLoanStatusData

# Loan Application Schemas
class LoanApplicationCreate(BaseModel):
    loan_type: Literal["Personal Loan", "Business Loan", "Home Loan", "Car Loan"]
    requested_amount: Decimal = Field(gt=0, description="Amount must be greater than 0")
    purpose: str
    employment_type: Literal["salaried", "self_employed", "business"]
    monthly_income: Decimal = Field(gt=0, description="Monthly income must be greater than 0")
    existing_emis: Decimal = Field(ge=0, default=0, description="Existing EMIs amount")
    
    @field_validator('requested_amount', 'monthly_income')
    @classmethod
    def validate_amounts(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class LoanApplicationResponse(BaseModel):
    status: str = "success"
    message: str = "Loan application submitted successfully"
    data: dict  # Contains application_id and reference_number

# Loan Details Schemas
class PaymentHistory(BaseModel):
    payment_date: date
    amount_paid: Decimal
    principal_component: Decimal
    interest_component: Decimal
    status: Literal["paid", "pending", "failed"]
    
    class Config:
        from_attributes = True

class UpcomingEMI(BaseModel):
    due_date: date
    emi_amount: Decimal
    principal_component: Decimal
    interest_component: Decimal
    
    class Config:
        from_attributes = True

class DetailedLoanInfo(BaseModel):
    loan_id: str
    account_number: str
    loan_type: Literal["Personal Loan", "Business Loan", "Home Loan", "Car Loan"]
    principal_amount: Decimal
    disbursed_amount: Decimal
    outstanding_balance: Decimal
    monthly_emi: Decimal
    next_due_date: date
    interest_rate: Decimal
    tenure_months: int
    tenure_remaining: int
    payment_history: List[PaymentHistory] = []
    upcoming_emis: List[UpcomingEMI] = []
    
    class Config:
        from_attributes = True

class LoanDetailsResponse(BaseModel):
    status: str = "success"
    data: DetailedLoanInfo

# Payment Schemas
class LoanPaymentCreate(BaseModel):
    loan_id: str
    payment_amount: Decimal = Field(gt=0, description="Payment amount must be greater than 0")
    payment_method: Literal["bank_transfer", "upi", "card"]
    payment_reference: str
    
    @field_validator('payment_amount')
    @classmethod
    def validate_payment_amount(cls, v):
        if v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        return v

class PaymentResponse(BaseModel):
    status: str = "success"
    message: str
    data: dict  # Contains payment details

# Document Upload Schema
class DocumentUpload(BaseModel):
    document_type: str  # Allow any document type
    file_name: str
    
# Cancel Application Schema
class CancelApplicationResponse(BaseModel):
    status: str = "success"
    message: str = "Application cancelled successfully"
