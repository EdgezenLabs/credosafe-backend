from sqlalchemy.orm import Session
from datetime import datetime, timedelta , timezone
from app.models import user as user_model
from app.models import tenant as tenant_model
from app.models import loan_product as lp_model
from app.models import application as app_model
from app.models import application_documents as doc_model
from app.models import Lead as lead_model
from app.models import payments as payment_model
from app.models import otp_codes as otp_model
from app.models import password_reset_token as reset_model
from app.core import security
from app.schemas import user_schema, tenant_schema, loan_schema, lead_schema, application_schema
import random
import secrets

# Users
def create_user(db: Session, user_in: user_schema.UserCreate):
    hashed = None
    if getattr(user_in, "password", None):
        hashed = security.hash_password(user_in.password)
    u = user_model.User(
        tenant_id=user_in.tenant_id,
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        password_hash=hashed,
        role=user_in.role,
        meta=user_in.meta or {}
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def get_user_by_email(db: Session, email: str):
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(user_model.User).filter(user_model.User.phone == phone).first()

def get_user(db: Session, user_id: str):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def update_user_password(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    user.password_hash = security.hash_password(password)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not user.password_hash:
        return None  # User hasn't set a password yet
    if not security.verify_password(password, user.password_hash):
        return None  # Wrong password
    if not user.is_active:
        return None  # User is deactivated
    return user

def list_users(db: Session, skip=0, limit=25, role=None):
    q = db.query(user_model.User)
    if role:
        q = q.filter(user_model.User.role == role)
    return q.offset(skip).limit(limit).all()

# Password Reset Tokens
def create_password_reset_token(db: Session, user_id: str):
    """Create a password reset token for a user"""
    # Invalidate any existing tokens for this user
    db.query(reset_model.PasswordResetToken).filter(
        reset_model.PasswordResetToken.user_id == user_id,
        reset_model.PasswordResetToken.used == False
    ).update({"used": True})
    
    # Create new token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Token expires in 1 hour
    
    reset_token = reset_model.PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        used=False
    )
    
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token

def get_password_reset_token(db: Session, token: str):
    """Get a valid password reset token"""
    return db.query(reset_model.PasswordResetToken).filter(
        reset_model.PasswordResetToken.token == token,
        reset_model.PasswordResetToken.used == False,
        reset_model.PasswordResetToken.expires_at > datetime.now(timezone.utc)
    ).first()

def use_password_reset_token(db: Session, token: str):
    """Mark a password reset token as used"""
    reset_token = get_password_reset_token(db, token)
    if reset_token:
        reset_token.used = True
        db.commit()
        return reset_token
    return None

# Tenants
def create_tenant(db: Session, payload: tenant_schema.TenantCreate):
    t = tenant_model.Tenant(
        name=payload.name,
        domain=payload.domain,
        logo_url=payload.logo_url,
        theme=payload.theme or {},
        config=payload.config or {}
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

def list_tenants(db: Session, skip=0, limit=25):
    return db.query(tenant_model.Tenant).offset(skip).limit(limit).all()

def get_tenant(db: Session, tenant_id: str):
    return db.query(tenant_model.Tenant).filter(tenant_model.Tenant.id == tenant_id).first()

# Loan product
def create_loan_product(db: Session, payload: loan_schema.LoanProductCreate):
    p = lp_model.LoanProduct(
        tenant_id=payload.tenant_id,
        name=payload.name,
        description=payload.description,
        interest_rate=payload.interest_rate,
        min_amount=payload.min_amount,
        max_amount=payload.max_amount,
        tenure_months=payload.tenure_months,
        active=payload.active
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def list_loan_products(db: Session, tenant_id: str = None, skip=0, limit=25):
    q = db.query(lp_model.LoanProduct)
    if tenant_id:
        q = q.filter(lp_model.LoanProduct.tenant_id == tenant_id)
    return q.offset(skip).limit(limit).all()

# Leads
def create_lead(db: Session, payload: lead_schema.LeadCreate):
    L = lead_model.Lead(
        tenant_id=payload.tenant_id,
        agent_id=payload.agent_id,
        customer_name=payload.customer_name,
        phone=payload.phone,
        email=payload.email,
        source=payload.source,
        status=payload.status,
        notes=payload.notes,
        next_followup=payload.next_followup
    )
    db.add(L)
    db.commit()
    db.refresh(L)
    return L

def list_leads(db: Session, tenant_id: str = None, agent_id: str = None, skip=0, limit=25):
    q = db.query(lead_model.Lead)
    if tenant_id:
        q = q.filter(lead_model.Lead.tenant_id == tenant_id)
    if agent_id:
        q = q.filter(lead_model.Lead.agent_id == agent_id)
    return q.offset(skip).limit(limit).all()

# Applications
def create_application(db: Session, payload: application_schema.ApplicationCreate):
    A = app_model.Application(
        tenant_id=payload.tenant_id,
        user_id=payload.user_id,
        agent_id=payload.agent_id,
        loan_product_id=payload.loan_product_id,
        amount_requested=payload.amount_requested,
        tenure=payload.tenure,
        notes=payload.notes
    )
    db.add(A)
    db.commit()
    db.refresh(A)
    return A

def get_application(db: Session, app_id: str):
    return db.query(app_model.Application).filter(app_model.Application.id == app_id).first()

def list_applications(db: Session, tenant_id: str = None, status: str = None, user_id: str = None, agent_id: str = None, skip=0, limit=25):
    q = db.query(app_model.Application)
    if tenant_id:
        q = q.filter(app_model.Application.tenant_id == tenant_id)
    if status:
        q = q.filter(app_model.Application.status == status)
    if user_id:
        q = q.filter(app_model.Application.user_id == user_id)
    if agent_id:
        q = q.filter(app_model.Application.agent_id == agent_id)
    return q.offset(skip).limit(limit).all()

def update_application_status(db: Session, app_id: str, status: str, notes: str = None):
    a = get_application(db, app_id)
    if not a:
        return None
    a.status = status
    if notes is not None:
        a.notes = notes
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

# Documents
def save_document(db: Session, application_id: str, uploaded_by: str, file_url: str, document_type: str, mime_type: str, size: int):
    d = doc_model.ApplicationDocument(
        application_id=application_id,
        uploaded_by=uploaded_by,
        document_type=document_type,
        file_url=file_url,
        mime_type=mime_type,
        size_bytes=size
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

def list_documents_for_application(db: Session, application_id: str):
    return db.query(doc_model.ApplicationDocument).filter(doc_model.ApplicationDocument.application_id == application_id).all()

def get_document_by_id(db: Session, document_id: str):
    """Get a single document by its ID"""
    return db.query(doc_model.ApplicationDocument).filter(doc_model.ApplicationDocument.id == document_id).first()

# Payments
def create_payment(db: Session, payload):
    p = payment_model.Payment(
        application_id=payload.application_id,
        tenant_id=payload.tenant_id,
        amount=payload.amount,
        method=payload.method,
        provider_reference=payload.provider_reference
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def list_payments(db: Session, application_id: str = None):
    q = db.query(payment_model.Payment)
    if application_id:
        q = q.filter(payment_model.Payment.application_id == application_id)
    return q.all()

# OTP
def create_otp(db: Session, principal: str, purpose: str, tenant_id: str = None, ttl_minutes: int = None):
    ttl = ttl_minutes or 5
    code = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=ttl)
    rec = otp_model.OTPCodes(
        tenant_id=tenant_id,
        purpose=purpose,
        principal=principal,
        code=code,
        expires_at=expires
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def verify_otp(db: Session, principal: str, code: str, purpose: str):
    rec = db.query(otp_model.OTPCodes).filter(
        otp_model.OTPCodes.principal == principal,
        otp_model.OTPCodes.purpose == purpose,
        otp_model.OTPCodes.used == False
    ).order_by(otp_model.OTPCodes.created_at.desc()).first()
    if not rec:
        return False
    if rec.code != code:
        return False
    if rec.expires_at < datetime.now(timezone.utc):
        return False
    rec.used = True
    db.add(rec)
    db.commit()
    return True

# Reports
from sqlalchemy import func
def applications_summary(db: Session, tenant_id: str = None, date_from=None, date_to=None):
    q = db.query(app_model.Application.status, func.count(app_model.Application.id)).group_by(app_model.Application.status)
    if tenant_id:
        q = q.filter(app_model.Application.tenant_id == tenant_id)
    rows = q.all()
    return [{"status": r[0], "count": r[1]} for r in rows]

# Loan Management CRUD Operations
from app.models.loan import Loan, LoanApplication, LoanDocument, LoanPayment, EMISchedule

def get_user_active_loan(db: Session, user_id: str):
    """Get user's active loan"""
    return db.query(Loan).filter(
        Loan.user_id == user_id,
        Loan.status.in_(["active", "overdue"])
    ).first()

def get_user_pending_application(db: Session, user_id: str):
    """Get user's pending loan application"""
    return db.query(LoanApplication).filter(
        LoanApplication.user_id == user_id,
        LoanApplication.status.in_(["under_review", "documents_pending", "approved"])
    ).first()

def create_loan_application(db: Session, application_data: dict):
    """Create a new loan application"""
    application = LoanApplication(**application_data)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

def update_loan_application_status(db: Session, application_id: str, status: str):
    """Update loan application status"""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if application:
        application.status = status
        db.commit()
        return application
    return None
