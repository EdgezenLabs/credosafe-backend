import uuid
import enum
from sqlalchemy import Column, Numeric, Integer, Date, TIMESTAMP, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class InstallmentStatus(str, enum.Enum):
    upcoming = "upcoming"
    due = "due"
    paid = "paid"
    overdue = "overdue"
    partial_paid = "partial_paid"

class LoanInstallment(Base):
    __tablename__ = "loan_installments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(PG_UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    
    # Installment Details
    installment_number = Column(Integer, nullable=False)  # 1, 2, 3... up to tenure_months
    due_date = Column(Date, nullable=False)
    emi_amount = Column(Numeric(10,2), nullable=False)
    principal_component = Column(Numeric(10,2), nullable=False)
    interest_component = Column(Numeric(10,2), nullable=False)
    
    # Payment Tracking
    amount_paid = Column(Numeric(10,2), nullable=True, default=0)
    paid_date = Column(Date, nullable=True)
    status = Column(Enum(InstallmentStatus), nullable=False, default=InstallmentStatus.upcoming)
    
    # Late Fee/Penalty
    penalty_amount = Column(Numeric(10,2), nullable=True, default=0)
    days_overdue = Column(Integer, nullable=True, default=0)
    
    # Metadata
    is_current = Column(Boolean, default=False)  # Current month's EMI
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    loan = relationship("Loan", back_populates="installments")

    def __repr__(self):
        return f"<LoanInstallment(id={self.id}, loan_id={self.loan_id}, installment_number={self.installment_number})>"