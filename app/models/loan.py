from sqlalchemy import Column, String, DateTime, Boolean, Integer, DECIMAL, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_number = Column(String(50), unique=True, nullable=False)
    loan_type = Column(String(50), nullable=False)  # Personal Loan, Business Loan, Home Loan, Car Loan
    principal_amount = Column(DECIMAL(15, 2), nullable=False)
    disbursed_amount = Column(DECIMAL(15, 2), nullable=False)
    outstanding_balance = Column(DECIMAL(15, 2), nullable=False)
    monthly_emi = Column(DECIMAL(10, 2), nullable=False)
    interest_rate = Column(DECIMAL(5, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    tenure_remaining = Column(Integer, nullable=False)
    next_due_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, overdue, completed, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reference_number = Column(String(50), unique=True, nullable=False)
    loan_type = Column(String(50), nullable=False)
    requested_amount = Column(DECIMAL(15, 2), nullable=False)
    purpose = Column(Text)
    employment_type = Column(String(20))  # salaried, self_employed, business
    monthly_income = Column(DECIMAL(10, 2))
    existing_emis = Column(DECIMAL(10, 2), default=0)
    current_step = Column(Integer, default=0)
    status = Column(String(20), nullable=False, default="under_review")  # under_review, documents_pending, approved, rejected, cancelled
    application_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LoanDocument(Base):
    __tablename__ = "loan_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # Any document type: aadhar, aadhaar, pan, income_proof, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="uploaded")  # uploaded, pending, verified, rejected
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class LoanPayment(Base):
    __tablename__ = "loan_payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount_paid = Column(DECIMAL(10, 2), nullable=False)
    principal_component = Column(DECIMAL(10, 2), nullable=False)
    interest_component = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(20))  # bank_transfer, upi, card
    payment_reference = Column(String(100))
    status = Column(String(20), nullable=False, default="paid")  # paid, pending, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EMISchedule(Base):
    __tablename__ = "emi_schedule"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)
    emi_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    emi_amount = Column(DECIMAL(10, 2), nullable=False)
    principal_component = Column(DECIMAL(10, 2), nullable=False)
    interest_component = Column(DECIMAL(10, 2), nullable=False)
    is_paid = Column(Boolean, default=False)
    payment_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
