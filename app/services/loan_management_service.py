from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional, List
from datetime import datetime, date
import uuid
import logging
from decimal import Decimal

from app.models.loan import Loan, LoanApplication, LoanDocument, LoanPayment, EMISchedule
from app.models.user import User

# Set up logging
logger = logging.getLogger(__name__)

from app.schemas.loan_management_schema import (
    LoanApplicationCreate, 
    LoanPaymentCreate,
    UserLoanStatusData,
    LoanDetails,
    PendingApplication,
    DocumentStatus,
    DocumentDetail,
    DetailedLoanInfo,
    PaymentHistory,
    UpcomingEMI
)

class LoanManagementService:
    
    @staticmethod
    def get_user_loan_status(db: Session, user_id: str) -> UserLoanStatusData:
        """Get user's current loan status to determine post-login routing"""
        
        # Convert user_id string to UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID format")
        
        # Check for active loans
        active_loan = db.query(Loan).filter(
            and_(
                Loan.user_id == user_uuid,
                Loan.status.in_(["active", "overdue"])
            )
        ).first()
        
        if active_loan:
            loan_details = LoanDetails(
                loan_id=str(active_loan.id),
                loan_type=active_loan.loan_type,
                principal_amount=active_loan.principal_amount,
                outstanding_balance=active_loan.outstanding_balance,
                monthly_emi=active_loan.monthly_emi,
                next_due_date=active_loan.next_due_date,
                interest_rate=active_loan.interest_rate,
                tenure_months=active_loan.tenure_months,
                tenure_remaining=active_loan.tenure_remaining,
                status=active_loan.status
            )
            
            return UserLoanStatusData(
                user_status="has_loan",
                loan_details=loan_details
            )
        
        # Check for pending applications (GET ALL, not just first one)
        pending_apps = db.query(LoanApplication).filter(
            and_(
                LoanApplication.user_id == user_uuid,
                LoanApplication.status.in_(["under_review", "documents_pending", "approved"])
            )
        ).order_by(desc(LoanApplication.created_at)).all()  # Get all applications, newest first
        
        if pending_apps:
            pending_applications_list = []
            
            for pending_app in pending_apps:
                # Get document status for each application
                documents = db.query(LoanDocument).filter(
                    LoanDocument.application_id == pending_app.id
                ).all()
                
                doc_status_list = [
                    DocumentStatus(
                        document_type=doc.document_type,
                        status=doc.status
                    ) for doc in documents
                ]
                
                # Get detailed document information
                document_details = [
                    DocumentDetail(
                        document_id=str(doc.id),
                        document_type=doc.document_type,
                        file_name=doc.file_name,
                        file_path=doc.file_path,
                        status=doc.status,
                        uploaded_at=doc.uploaded_at
                    ) for doc in documents
                ]
                
                pending_application = PendingApplication(
                    application_id=str(pending_app.id),
                    loan_type=pending_app.loan_type,
                    requested_amount=pending_app.requested_amount,
                    application_date=pending_app.created_at.date(),
                    current_step=pending_app.current_step,
                    status=pending_app.status,
                    documents_required=doc_status_list,
                    documents=document_details  # Include actual document details
                )
                
                pending_applications_list.append(pending_application)
            
            return UserLoanStatusData(
                user_status="pending_application",
                pending_application=pending_applications_list[0],  # Keep first one for backward compatibility
                pending_applications=pending_applications_list     # New field with all applications
            )
        
        # New user with no loans or applications
        return UserLoanStatusData(user_status="new_user")
    
    @staticmethod
    def save_application_document(db: Session, application_id: str, document_type: str, file_name: str, user_id) -> dict:
        """Save uploaded document to database"""
        
        # Convert application_id to UUID
        try:
            app_uuid = uuid.UUID(application_id)
        except ValueError:
            raise ValueError("Invalid application ID format")
        
        # Verify application exists and belongs to user
        application = db.query(LoanApplication).filter(
            and_(
                LoanApplication.id == app_uuid,
                LoanApplication.user_id == user_id
            )
        ).first()
        
        if not application:
            raise ValueError("Application not found or does not belong to user")
        
        # Create file path (for now, just store file name - in production, save to actual storage)
        file_path = f"/uploads/documents/{application_id}/{file_name}"
        
        # Create document record
        document = LoanDocument(
            application_id=app_uuid,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            status="uploaded"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return {
            "document_id": str(document.id),
            "application_id": application_id,
            "document_type": document_type,
            "file_name": file_name,
            "file_path": file_path,
            "status": "uploaded",
            "uploaded_at": document.uploaded_at.isoformat()
        }
    
    @staticmethod
    def create_loan_application(db: Session, user_id: str, application_data: LoanApplicationCreate) -> dict:
        """Create a new loan application"""
        
        logger.info(f"=== CREATE LOAN APPLICATION DEBUG ===")
        logger.info(f"Received user_id: {user_id} (type: {type(user_id)})")
        logger.info(f"Application data: {application_data}")
        
        # Convert user_id string to UUID
        try:
            user_uuid = uuid.UUID(user_id)
            logger.info(f"Converted to UUID: {user_uuid} (type: {type(user_uuid)})")
        except ValueError as e:
            logger.error(f"UUID conversion failed: {e}")
            raise ValueError("Invalid user ID format")
        
        # Verify user exists
        try:
            user = db.query(User).filter(User.id == user_uuid).first()
            if not user:
                logger.error(f"User not found with ID: {user_uuid}")
                raise ValueError("User not found")
            logger.info(f"User found: {user.email}")
        except Exception as e:
            logger.error(f"User lookup failed: {e}")
            raise
        
        # Generate reference number
        reference_number = f"CRD{datetime.now().year}{str(uuid.uuid4())[:8].upper()}"
        logger.info(f"Generated reference number: {reference_number}")
        
        # Create application object
        try:
            logger.info("Creating LoanApplication object...")
            new_application = LoanApplication(
                user_id=user_uuid,
                reference_number=reference_number,
                loan_type=application_data.loan_type,
                requested_amount=application_data.requested_amount,
                purpose=application_data.purpose,
                employment_type=application_data.employment_type,
                monthly_income=application_data.monthly_income,
                existing_emis=application_data.existing_emis,
                current_step=1,
                status="under_review",
                application_data={
                    "purpose": application_data.purpose,
                    "employment_type": application_data.employment_type,
                    "monthly_income": float(application_data.monthly_income),
                    "existing_emis": float(application_data.existing_emis)
                }
            )
            logger.info("LoanApplication object created successfully")
        except Exception as e:
            logger.error(f"Failed to create LoanApplication object: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # Add to database
        try:
            logger.info("Adding to database session...")
            db.add(new_application)
            logger.info("Committing to database...")
            db.commit()
            logger.info("Refreshing object...")
            db.refresh(new_application)
            logger.info("Database operations completed successfully")
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            db.rollback()
            raise
        
        result = {
            "application_id": str(new_application.id),
            "reference_number": new_application.reference_number
        }
        logger.info(f"Returning result: {result}")
        return result
    
    @staticmethod
    def cancel_loan_application(db: Session, user_id: str, application_id: str) -> bool:
        """Cancel a pending loan application"""
        
        application = db.query(LoanApplication).filter(
            and_(
                LoanApplication.id == application_id,
                LoanApplication.user_id == user_id,
                LoanApplication.status.in_(["under_review", "documents_pending"])
            )
        ).first()
        
        if not application:
            return False
        
        application.status = "cancelled"
        db.commit()
        return True
    
    @staticmethod
    def get_loan_details(db: Session, user_id: str, loan_id: str) -> Optional[DetailedLoanInfo]:
        """Get detailed loan information for dashboard"""
        
        loan = db.query(Loan).filter(
            and_(
                Loan.id == loan_id,
                Loan.user_id == user_id
            )
        ).first()
        
        if not loan:
            return None
        
        # Get payment history (last 10 payments)
        payments = db.query(LoanPayment).filter(
            LoanPayment.loan_id == loan_id
        ).order_by(desc(LoanPayment.payment_date)).limit(10).all()
        
        payment_history = [
            PaymentHistory(
                payment_date=payment.payment_date,
                amount_paid=payment.amount_paid,
                principal_component=payment.principal_component,
                interest_component=payment.interest_component,
                status=payment.status
            ) for payment in payments
        ]
        
        # Get upcoming EMIs (next 3 EMIs)
        upcoming_emis_query = db.query(EMISchedule).filter(
            and_(
                EMISchedule.loan_id == loan_id,
                EMISchedule.is_paid == False,
                EMISchedule.due_date >= date.today()
            )
        ).order_by(EMISchedule.due_date).limit(3).all()
        
        upcoming_emis = [
            UpcomingEMI(
                due_date=emi.due_date,
                emi_amount=emi.emi_amount,
                principal_component=emi.principal_component,
                interest_component=emi.interest_component
            ) for emi in upcoming_emis_query
        ]
        
        return DetailedLoanInfo(
            loan_id=str(loan.id),
            account_number=loan.account_number,
            loan_type=loan.loan_type,
            principal_amount=loan.principal_amount,
            disbursed_amount=loan.disbursed_amount,
            outstanding_balance=loan.outstanding_balance,
            monthly_emi=loan.monthly_emi,
            next_due_date=loan.next_due_date,
            interest_rate=loan.interest_rate,
            tenure_months=loan.tenure_months,
            tenure_remaining=loan.tenure_remaining,
            payment_history=payment_history,
            upcoming_emis=upcoming_emis
        )
    
    @staticmethod
    def process_loan_payment(db: Session, user_id: str, payment_data: LoanPaymentCreate) -> dict:
        """Process a loan payment"""
        
        # Verify loan belongs to user
        loan = db.query(Loan).filter(
            and_(
                Loan.id == payment_data.loan_id,
                Loan.user_id == user_id,
                Loan.status == "active"
            )
        ).first()
        
        if not loan:
            raise ValueError("Loan not found or not active")
        
        # Get next EMI to calculate principal/interest split
        next_emi = db.query(EMISchedule).filter(
            and_(
                EMISchedule.loan_id == payment_data.loan_id,
                EMISchedule.is_paid == False
            )
        ).order_by(EMISchedule.due_date).first()
        
        if not next_emi:
            raise ValueError("No pending EMI found")
        
        # Create payment record
        payment = LoanPayment(
            loan_id=payment_data.loan_id,
            payment_date=date.today(),
            amount_paid=payment_data.payment_amount,
            principal_component=next_emi.principal_component,
            interest_component=next_emi.interest_component,
            payment_method=payment_data.payment_method,
            payment_reference=payment_data.payment_reference,
            status="paid"
        )
        
        db.add(payment)
        
        # Update EMI as paid
        next_emi.is_paid = True
        next_emi.payment_date = date.today()
        
        # Update loan balance
        loan.outstanding_balance -= next_emi.principal_component
        loan.tenure_remaining -= 1
        
        # Update next due date
        next_upcoming_emi = db.query(EMISchedule).filter(
            and_(
                EMISchedule.loan_id == payment_data.loan_id,
                EMISchedule.is_paid == False
            )
        ).order_by(EMISchedule.due_date).first()
        
        if next_upcoming_emi:
            loan.next_due_date = next_upcoming_emi.due_date
        else:
            # All EMIs paid, mark loan as completed
            loan.status = "completed"
        
        db.commit()
        
        return {
            "payment_id": str(payment.id),
            "amount_paid": float(payment.amount_paid),
            "remaining_balance": float(loan.outstanding_balance),
            "next_due_date": loan.next_due_date.isoformat() if loan.status == "active" else None
        }

    @staticmethod
    def save_application_document(db: Session, application_id: str, document_type: str, file_name: str, user_id: str, file_path: str) -> dict:
        """Save document for loan application"""
        
        logger.info(f"=== SAVE APPLICATION DOCUMENT DEBUG ===")
        logger.info(f"Application ID: {application_id}")
        logger.info(f"Document type: {document_type}")
        logger.info(f"File name: {file_name}")
        logger.info(f"File path: {file_path}")
        logger.info(f"User ID: {user_id}")
        
        try:
            # Convert application_id and user_id to UUID (handle both string and UUID input)
            if isinstance(application_id, str):
                application_uuid = uuid.UUID(application_id)
            else:
                application_uuid = application_id
                
            if isinstance(user_id, str):
                user_uuid = uuid.UUID(user_id)
            else:
                user_uuid = user_id
            
            # Verify application exists and belongs to user
            application = db.query(LoanApplication).filter(
                and_(
                    LoanApplication.id == application_uuid,
                    LoanApplication.user_id == user_uuid
                )
            ).first()
            
            if not application:
                raise ValueError("Application not found or doesn't belong to user")
            
            # Create document record with actual file path
            document = LoanDocument(
                application_id=application_uuid,
                user_id=user_uuid,
                document_type=document_type,
                file_name=file_name,
                file_path=file_path,  # Use the actual file path from disk
                status="uploaded"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Document saved successfully: {document.id}")
            
            return {
                "document_id": str(document.id),
                "document_type": document_type,
                "file_name": file_name,
                "file_path": file_path,
                "status": "uploaded",
                "uploaded_at": document.uploaded_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_document_by_id(db: Session, document_id: str, user_id: str) -> dict:
        """Get a document by ID, ensuring it belongs to the user"""
        
        try:
            # Convert to UUID
            if isinstance(document_id, str):
                doc_uuid = uuid.UUID(document_id)
            else:
                doc_uuid = document_id
                
            if isinstance(user_id, str):
                user_uuid = uuid.UUID(user_id)
            else:
                user_uuid = user_id
            
            # Get document and verify it belongs to user
            document = db.query(LoanDocument).filter(
                and_(
                    LoanDocument.id == doc_uuid,
                    LoanDocument.user_id == user_uuid
                )
            ).first()
            
            if not document:
                return None
            
            return {
                "document_id": str(document.id),
                "document_type": document.document_type,
                "file_name": document.file_name,
                "file_path": document.file_path,
                "status": document.status,
                "uploaded_at": document.uploaded_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
