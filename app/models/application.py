import uuid
import enum
from sqlalchemy import Column, Text, Numeric, Integer, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.core.database import Base

class ApplicationStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    withdrawn = "withdrawn"
    disbursed = "disbursed"

class Application(Base):
    __tablename__ = "applications"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    agent_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    loan_product_id = Column(PG_UUID(as_uuid=True), ForeignKey("loan_products.id", ondelete="SET NULL"), nullable=True)
    amount_requested = Column(Numeric(15,2), nullable=False)
    tenure = Column(Integer, nullable=True)
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.submitted)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
