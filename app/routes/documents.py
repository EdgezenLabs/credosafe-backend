from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.files import save_upload_file
from app.core.config import settings
from app.crud import crud
import os

router = APIRouter()

@router.post("/upload", status_code=201)
def upload_document(application_id: str = Form(...), document_type: str = Form(...), uploaded_by: str = Form(None), file: UploadFile = File(...), db: Session = Depends(get_db)):
    path, size = save_upload_file(file, settings.UPLOAD_DIR)
    rec = crud.save_document(db, application_id=application_id, uploaded_by=uploaded_by, file_url=path, document_type=document_type, mime_type=file.content_type, size=size)
    return rec

@router.get("/application/{application_id}", response_model=dict)
def list_doc(application_id: str, db: Session = Depends(get_db)):
    docs = crud.list_documents_for_application(db, application_id)
    return {"total": len(docs), "items": docs}

