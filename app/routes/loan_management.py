from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import logging
import os
from app.core.database import get_db
from app.core.security import get_current_user_email
from app.services.loan_management_service import LoanManagementService
from app.schemas.loan_management_schema import (
    UserLoanStatusResponse,
    LoanApplicationCreate,
    LoanApplicationResponse,
    CancelApplicationResponse,
    LoanDetailsResponse,
    LoanPaymentCreate,
    PaymentResponse
)
from app.crud import crud
from typing import Dict

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/user/loan-status", response_model=UserLoanStatusResponse)
def get_user_loan_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    """Get user's current loan status to determine post-login routing"""
    
    # Get user by email
    user = crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    loan_status_data = LoanManagementService.get_user_loan_status(db, str(user.id))
    
    return UserLoanStatusResponse(data=loan_status_data)

@router.post("/loan/apply", response_model=LoanApplicationResponse)
def apply_for_loan(
    application_data: LoanApplicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    """Submit new loan application"""
    
    logger.info(f"=== LOAN APPLICATION ROUTE DEBUG ===")
    logger.info(f"Current user from JWT: {current_user}")
    logger.info(f"Application data received: {application_data}")
    
    # Get user by email
    try:
        user = crud.get_user_by_email(db, current_user["email"])
        if not user:
            logger.error(f"User not found with email: {current_user['email']}")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User found: ID={user.id}, email={user.email}")
    except Exception as e:
        logger.error(f"User lookup failed: {e}")
        raise HTTPException(status_code=500, detail=f"User lookup failed: {str(e)}")
    
    try:
        logger.info(f"Calling LoanManagementService.create_loan_application with user_id={str(user.id)}")
        result = LoanManagementService.create_loan_application(
            db, str(user.id), application_data
        )
        logger.info(f"Service returned: {result}")
        
        return LoanApplicationResponse(data=result)
    
    except Exception as e:
        logger.error(f"Loan application creation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/loan/application/{application_id}/cancel", response_model=CancelApplicationResponse)
def cancel_loan_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    """Cancel pending loan application"""
    
    # Get user by email
    user = crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = LoanManagementService.cancel_loan_application(
        db, str(user.id), application_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Application not found or cannot be cancelled"
        )
    
    return CancelApplicationResponse()

@router.get("/loan/details/{loan_id}", response_model=LoanDetailsResponse)
def get_loan_details(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    """Get detailed loan information for dashboard"""
    
    # Get user by email
    user = crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    loan_details = LoanManagementService.get_loan_details(
        db, str(user.id), loan_id
    )
    
    if not loan_details:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    return LoanDetailsResponse(data=loan_details)

@router.post("/loan/payment", response_model=PaymentResponse)
def process_loan_payment(
    payment_data: LoanPaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    """Process loan payment"""
    
    # Get user by email
    user = crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        result = LoanManagementService.process_loan_payment(
            db, str(user.id), payment_data
        )
        
        return PaymentResponse(
            message="Payment processed successfully",
            data=result
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment processing failed")

@router.post("/loan/application/{application_id}/documents")
def upload_application_document(
    application_id: str,
    document_type: str = Form(..., description="Document type: aadhar, pan"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    """Upload documents for loan application"""
    
    # Get user by email
    user = crud.get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log what we received for debugging
    logger.info(f"=== DOCUMENT UPLOAD DEBUG ===")
    logger.info(f"Received document_type: '{document_type}' (type: {type(document_type)})")
    logger.info(f"Received file: '{file.filename}' (content_type: {file.content_type})")
    logger.info(f"Application ID: {application_id}")
    
    # NO VALIDATION - Accept everything for now
    # TODO: Add validation back later if needed
    
    # Save document to database
    try:
        document_data = LoanManagementService.save_application_document(
            db, application_id, document_type, file.filename, str(user.id)
        )
        logger.info(f"Document saved to database: {document_data}")
        
        return {
            "status": "success",
            "message": "Document uploaded successfully",
            "data": document_data
        }
    except Exception as e:
        logger.error(f"Failed to save document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")