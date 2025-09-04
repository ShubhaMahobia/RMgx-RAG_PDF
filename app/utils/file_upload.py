import os
import logging
from fastapi import UploadFile
import shutil
import uuid

# Get logger for this module
logger = logging.getLogger(__name__)

UPLOAD_DIR = "data/uploads"

def save_pdf_file(file: UploadFile) -> str:
    """Save uploaded PDF to the uploads folder with a unique filename and return its path."""
    logger.info(f"Saving uploaded file: {file.filename}")
    
    try:
        if not os.path.exists(UPLOAD_DIR):
            logger.debug(f"Creating upload directory: {UPLOAD_DIR}")
            os.makedirs(UPLOAD_DIR)

        _, ext = os.path.splitext(file.filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        logger.debug(f"Generated unique filename: {unique_filename}")
        logger.debug(f"Full file path: {file_path}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved successfully at: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}: {str(e)}")
        raise
