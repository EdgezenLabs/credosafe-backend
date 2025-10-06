import uuid
from sqlalchemy import Column, Integer, DateTime, Numeric, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.core.database import Base

class Installment(Base):
    __tablename__ = "installments"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(PG_UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"))
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    installment_no = Column(Integer)
    due_date = Column(TIMESTAMP(timezone=True))
    principal_amount = Column(Numeric(15,2))
    interest_amount = Column(Numeric(15,2))
    total_amount = Column(Numeric(15,2))
    paid = Column(Boolean, default=False)
    paid_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
