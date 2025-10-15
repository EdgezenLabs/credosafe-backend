# app/models/payment.py

# 1. Import necessary components
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime

# Assuming Base and TimestampMixin are correctly defined and exported from .base
from app.core.database import Base
from .base import TimestampMixin 


class Payment(TimestampMixin, Base):
    """
    SQLAlchemy model for the 'payments' table.
    Inherits from Base (SQLAlchemy declarative base) and TimestampMixin (for created_at/updated_at).
    """
    
    # Define the table name
    __tablename__ = "payments"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key linking to the Application model
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)
    
    # Payment details
    payment_amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    transaction_id = Column(String(100), unique=True, index=True)
    
    # Status can be 'SUCCESS', 'PENDING', 'FAILED', etc.
    status = Column(String(50), default="PENDING", nullable=False)

# Note: The structure of your model will depend entirely on your business requirements.
# The fields above are common examples for a payment record.