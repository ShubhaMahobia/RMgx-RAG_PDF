from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.file_upload import save_pdf_file

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_path = save_pdf_file(file)
    return {"message": "File uploaded successfully", "file_path": file_path}
