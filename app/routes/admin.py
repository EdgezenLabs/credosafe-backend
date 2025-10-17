from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_email
from app.models.loan import LoanApplication, LoanDocument
from app.models.user import User
from app.crud import crud

router = APIRouter(prefix="/admin", tags=["Admin"])

# Admin-only: List all loan applications with user name and documents
@router.get("/loan-applications")
def list_loan_applications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    apps = db.query(LoanApplication).all()
    result = []
    for app in apps:
        user = db.query(User).filter_by(id=app.user_id).first()
        docs = db.query(LoanDocument).filter_by(application_id=app.id).all()
        result.append({
            "application_id": str(app.id),
            "user_name": user.name if user else None,
            "loan_type": app.loan_type,
            "requested_amount": float(app.requested_amount),
            "status": app.status,
            "documents": [
                {
                    "document_id": str(doc.id),
                    "document_type": doc.document_type,
                    "file_name": doc.file_name,
                    "status": doc.status
                } for doc in docs
            ]
        })
    return {"total": len(result), "items": result}

# Admin-only: Approve a loan application
@router.put("/loan-application/{application_id}/approve")
def approve_loan_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_email)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    app = db.query(LoanApplication).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status == "approved":
        return {"status": "already_approved", "message": "Application already approved"}
    app.status = "approved"
    db.commit()
    return {"status": "success", "message": "Loan application approved", "application_id": application_id}
