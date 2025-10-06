import uuid
from sqlalchemy import Column, Text, JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    domain = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    theme = Column(JSON, default={})
    config = Column(JSON, default={})
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
