import uuid
import enum
from sqlalchemy import Column, Text, Numeric, Date, TIMESTAMP, ForeignKey, String, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PaymentStatus(str, enum.Enum):
    paid = "paid"
    pending = "pending"
    failed = "failed"
    cancelled = "cancelled"

class PaymentMethod(str, enum.Enum):
    bank_transfer = "bank_transfer"
    upi = "upi"
    card = "card"
    cash = "cash"
    cheque = "cheque"

class LoanPayment(Base):
    __tablename__ = "loan_payments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(PG_UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    
    # Payment Details
    payment_date = Column(Date, nullable=False)
    amount_paid = Column(Numeric(10,2), nullable=False)
    principal_component = Column(Numeric(10,2), nullable=False)
    interest_component = Column(Numeric(10,2), nullable=False)
    penalty_component = Column(Numeric(10,2), nullable=True, default=0)
    
    # Payment Method and Reference
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_reference = Column(String(255), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    
    # Status
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    loan = relationship("Loan", back_populates="payments")
    user = relationship("User")

    def __repr__(self):
        return f"<LoanPayment(id={self.id}, loan_id={self.loan_id}, amount={self.amount_paid})>"