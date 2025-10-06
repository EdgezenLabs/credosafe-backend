# D:\Credosafe FastAPI\credosafe-backend\app\models\base.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
# ... other necessary imports (like from typing)

Base = declarative_base() # You likely have this correct now

# --> CRITICAL: Ensure this class is defined:
class TimestampMixin:
    """Mixin for common timestamp fields."""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

# ... rest of the file