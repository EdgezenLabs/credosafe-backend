# app/models/lead.py

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from uuid import uuid4
from .base import Base, TimestampMixin

class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    agent_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    source = Column(String)
    status = Column(String, default="new")
    notes = Column(String)
    next_followup = Column(DateTime(timezone=True))

    tenant = relationship("Tenant", back_populates="leads")
    agent = relationship("User", foreign_keys=[agent_id], back_populates="leads_managed")