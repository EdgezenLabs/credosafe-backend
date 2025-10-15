import uuid
import enum
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, String, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class DocumentStatus(str, enum.Enum):
    uploaded = "uploaded"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"

class DocumentType(str, enum.Enum):
    income_proof = "income_proof"
    identity_proof = "identity_proof" 
    address_proof = "address_proof"
    bank_statement = "bank_statement"
    salary_slip = "salary_slip"
    itr = "itr"
    business_registration = "business_registration"
    property_documents = "property_documents"
    other = "other"

class LoanDocument(Base):
    __tablename__ = "loan_documents"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(PG_UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    
    # Document Details
    document_type = Column(Enum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(String(50), nullable=True)  # e.g., "2.5 MB"
    mime_type = Column(String(100), nullable=True)  # e.g., "application/pdf"
    
    # Status and Verification
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.uploaded)
    uploaded_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Who uploaded
    verified_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Who verified
    
    # Metadata
    notes = Column(Text, nullable=True)  # Verification notes or rejection reason
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    verified_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relationships
    application = relationship("Application")
    user = relationship("User", foreign_keys=[user_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])
    verifier = relationship("User", foreign_keys=[verified_by])

    def __repr__(self):
        return f"<LoanDocument(id={self.id}, type={self.document_type}, status={self.status})>"