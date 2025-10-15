# app/models/__init__.py

# NOTE: This file must import all model classes for SQLAlchemy to find them 
# when calling Base.metadata.create_all()

from app.core.database import Base
from .tenant import Tenant
from .user import User
from .loan_product import LoanProduct
from .lead import Lead
from .application import Application
from .application_documents import ApplicationDocument
from .loan import Loan, LoanApplication, LoanDocument, LoanPayment, EMISchedule
# Include other models not explicitly listed in your folder view, but needed for the DB structure
from .payments import Payment
from .installment import Installment
from .audit_logs import AuditLog