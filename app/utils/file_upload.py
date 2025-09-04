import os
from fastapi import UploadFile
import shutil
import uuid

UPLOAD_DIR = "data/uploads"

def save_pdf_file(file: UploadFile) -> str:
    """Save uploaded PDF to the uploads folder with a unique filename and return its path."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


    _, ext = os.path.splitext(file.filename)
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path
