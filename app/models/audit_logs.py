import uuid
from sqlalchemy import Column, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), nullable=True)
    user_id = Column(PG_UUID(as_uuid=True), nullable=True)
    action = Column(Text, nullable=True)
    object_type = Column(Text, nullable=True)
    object_id = Column(PG_UUID(as_uuid=True), nullable=True)
    meta = Column(JSON, default={})
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
