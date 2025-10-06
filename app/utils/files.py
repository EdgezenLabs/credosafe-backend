import os
from uuid import uuid4
from fastapi import UploadFile
from app.core.config import settings

def save_upload_file(upload_file: UploadFile, upload_dir: str = None):
    directory = upload_dir or settings.UPLOAD_DIR
    os.makedirs(directory, exist_ok=True)
    ext = ""
    if upload_file.filename:
        ext = "." + upload_file.filename.split(".")[-1] if "." in upload_file.filename else ""
    filename = f"{uuid4().hex}{ext}"
    path = os.path.join(directory, filename)
    with open(path, "wb") as f:
        content = upload_file.file.read()
        f.write(content)
        size = len(content)
    return path, size
