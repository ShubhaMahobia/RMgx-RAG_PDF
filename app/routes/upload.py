from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.file_upload import save_pdf_file
from app.services.pdf_loader import PDFLoader
from app.services.embedding import EmbeddingModel
from app.services.vectore_store import VectorStoreHandler
from app.config import Config
from dotenv import load_dotenv
import os
import logging
from from_root import from_root

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, process it (extract -> chunk -> embed -> save to Chroma).
    """
    logger.info(f"Starting PDF upload process for file: {file.filename}")
    
    if not file.filename.endswith(".pdf"):
        logger.warning(f"Rejected non-PDF file: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        # 1. Save uploaded file
        logger.debug("Saving uploaded file")
        file_path = save_pdf_file(file)
        logger.info(f"File saved successfully at: {file_path}")

        # 2. Load PDF -> extract text
        logger.debug("Loading PDF content")
        pdf_loader = PDFLoader(file_path)
        documents = pdf_loader.load()

        if not documents:
            logger.error("No text content found in PDF")
            raise HTTPException(status_code=400, detail="No text found in PDF.")

        # 3. Split into chunks
        logger.debug("Splitting documents into chunks")
        chunks = pdf_loader.split(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        logger.info(f"Created {len(chunks)} chunks from PDF")

        # 4. Initialize embedding model
        logger.debug("Initializing embedding model")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("Google API key not found in environment")
            raise HTTPException(status_code=500, detail="Google API key not configured.")

        embedder = EmbeddingModel(api_key=google_api_key)
        logger.info("Embedding model initialized successfully")

        # 5. Save chunks into Chroma vectorstore
        logger.debug("Saving documents to vector store")
        vs_handler = VectorStoreHandler(persist_dir="data/chroma")
        vs_handler.save_documents(chunks, embedder.model)
        logger.info("Documents saved to vector store successfully")

        logger.info(f"PDF upload and processing completed successfully for: {file.filename}")
        return {
            "message": "File uploaded and processed successfully",
            "file_name": file.filename,
            "total_chunks": len(chunks),
            "vectorstore_path": vs_handler.persist_dir
        }
        
    except Exception as e:
        logger.error(f"Error during PDF upload process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
