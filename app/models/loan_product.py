import uuid
from sqlalchemy import Column, Text, Numeric, Integer, Boolean, ARRAY, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.core.database import Base

class LoanProduct(Base):
    __tablename__ = "loan_products"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    interest_rate = Column(Numeric(5,2), nullable=True)
    min_amount = Column(Numeric(15,2), nullable=True)
    max_amount = Column(Numeric(15,2), nullable=True)
    tenure_months = Column(ARRAY(Integer), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
