from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.services.pdf_loader import PDFLoader
from app.services.embedding import EmbeddingModel
from app.services.pinecone_store import PineconeVectorStoreHandler
from app.services.storage.storage import get_storage
from app.config import Config
from app.models.chat import DeleteRequest, DeleteResponse, ResetRequest, ResetResponse
from dotenv import load_dotenv
import os
import logging
import tempfile
import shutil
from datetime import datetime

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Upload multiple PDFs, process them (extract -> chunk -> embed -> save to pinecone).
    Files are stored in S3 and metadata is added for differentiation.
    """
    logger.info(f"Starting upload process for {len(files)} files")

    uploaded_files = []
    all_chunks = []

    try:
        storage = get_storage()  

        for file in files:
            if not file.filename.endswith(".pdf"):
                logger.warning(f"Rejected non-PDF file: {file.filename}")
                raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF file")

            # 1. Save uploaded file locally first for processing
            logger.debug(f"Processing {file.filename} locally")
            
            # Create a temporary file to save the uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_file_path = temp_file.name
            
            original_filename = file.filename
            uploaded_files.append(original_filename)
            logger.info(f"File saved locally for processing: {original_filename}")

            # 2. Load PDF -> extract text
            logger.debug("Loading PDF content")
            pdf_loader = PDFLoader(temp_file_path)
            documents = pdf_loader.load()

            if not documents:
                logger.error(f"No text content found in {original_filename}")
                raise HTTPException(status_code=400, detail=f"No text found in {original_filename}")

            # 3. Split into chunks
            logger.debug("Splitting documents into chunks")
            chunks = pdf_loader.split(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP
            )
            logger.info(f"Created {len(chunks)} chunks for {original_filename}")
            

            # 4. Upload processed file to S3
            logger.debug(f"Uploading {original_filename} to S3")
            # Reset file pointer and upload to S3
            file.file.seek(0)
            file_info = storage.save_upload(file)
            s3_key = file_info["key"]
            logger.info(f"File uploaded to S3: s3://{file_info['bucket']}/{s3_key}")

            # 5. Add metadata (for differentiation)
            for idx, chunk in enumerate(chunks):
                chunk.metadata["file_name"] = original_filename
                chunk.metadata["chunk_id"] = idx
                chunk.metadata["page_number"] = chunk.metadata.get("page", None)
                chunk.metadata["s3_key"] = s3_key  # so you can fetch later if needed

            all_chunks.extend(chunks)
            
            # 6. Clean up temporary file
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")

        # 7. Initialize embedding model (once for all files)
        logger.debug("Initializing embedding model")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("Google API key not found in environment")
            raise HTTPException(status_code=500, detail="Google API key not configured.")

        embedder = EmbeddingModel(api_key=google_api_key)
        logger.info("Embedding model initialized successfully")

        # 8. Save chunks into Pinecone vectorstore
        logger.debug("Saving all documents to Pinecone vector store")
        vs_handler = PineconeVectorStoreHandler()
        vs_handler.save_documents(all_chunks, embedder.model)
        logger.info(f"Saved {len(all_chunks)} chunks to Pinecone vector store successfully")

        return {
            "message": "Files uploaded and processed successfully",
            "uploaded_files": uploaded_files,
            "total_chunks": len(all_chunks),
            "vectorstore": "pinecone",
            "index_name": vs_handler.index_name,
            "namespace": vs_handler.namespace
        }

    except Exception as e:
        logger.error(f"Error during upload process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


@router.get("/files")
def list_uploaded_files():
    """
    List all uploaded files stored in S3.
    Returns the S3 keys of uploaded PDFs.
    """
    try:
        storage = get_storage()  
        keys = storage.list_files()  

        logger.info(f"Fetched {len(keys)} files from S3")
        return {
            "total_files": len(keys),
            "files": keys
        }

    except Exception as e:
        logger.exception("Failed to list files from S3")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/delete", response_model=DeleteResponse)
async def delete_file(request: DeleteRequest):
    """
    Delete a PDF file from S3 bucket using its S3 key.
    Also removes associated vectors from Pinecone.
    """
    logger.info(f"Starting delete process for S3 key: {request.s3_key}")
    
    try:
        storage = get_storage()
        
        # 1. Delete file from S3
        logger.debug(f"Deleting file from S3: {request.s3_key}")
        storage.delete(request.s3_key)
        logger.info(f"File deleted from S3: {request.s3_key}")
        
        # 2. Remove associated vectors from Pinecone
        logger.debug("Removing associated vectors from Pinecone")
        try:
            vs_handler = PineconeVectorStoreHandler()
            deleted_count = vs_handler.delete_vectors_by_metadata({"s3_key": request.s3_key})
            logger.info(f"Successfully deleted {deleted_count} vectors from Pinecone for s3_key: {request.s3_key}")
            
        except Exception as pinecone_error:
            logger.warning(f"Failed to delete vectors from Pinecone: {str(pinecone_error)}")
            # Continue with S3 deletion even if Pinecone deletion fails
        
        # Extract filename from S3 key for response
        filename = request.s3_key.split('/')[-1] if '/' in request.s3_key else request.s3_key
        
        return DeleteResponse(
            message="File deleted successfully from S3",
            deleted_file=filename,
            s3_key=request.s3_key,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error during delete process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")




@router.post("/reset", response_model=ResetResponse)
async def reset_index(request: ResetRequest):
    """
    Reset the entire index by deleting all files from S3 and all vectors from Pinecone.
    This is a destructive operation that requires explicit confirmation.
    """
    logger.warning("Reset index operation requested")
    
    # Safety check - require explicit confirmation
    if not request.confirm:
        logger.warning("Reset operation rejected - confirmation required")
        raise HTTPException(
            status_code=400, 
            detail="Reset operation requires explicit confirmation. Set 'confirm': true in request body."
        )
    
    logger.info("Starting complete index reset operation")
    
    try:
        s3_files_deleted = 0
        pinecone_vectors_deleted = 0
        errors = []
        
        # 1. Delete all files from S3
        logger.info("Step 1: Deleting all files from S3")
        try:
            storage = get_storage()
            s3_files_deleted = storage.delete_all_files()
            logger.info(f"Successfully deleted {s3_files_deleted} files from S3")
        except Exception as s3_error:
            error_msg = f"S3 deletion failed: {str(s3_error)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # 2. Delete all vectors from Pinecone
        logger.info("Step 2: Deleting all vectors from Pinecone")
        try:
            vs_handler = PineconeVectorStoreHandler()
            pinecone_vectors_deleted = vs_handler.delete_all_vectors()
            logger.info(f"Successfully deleted {pinecone_vectors_deleted} vectors from Pinecone")
        except Exception as pinecone_error:
            error_msg = f"Pinecone deletion failed: {str(pinecone_error)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # 3. Prepare response
        success = len(errors) == 0
        message = "Index reset completed successfully" if success else "Index reset completed with some errors"
        
        if errors:
            message += f". Errors: {'; '.join(errors)}"
        
        logger.info(f"Reset operation completed. S3: {s3_files_deleted} files, Pinecone: {pinecone_vectors_deleted} vectors")
        
        return ResetResponse(
            message=message,
            s3_files_deleted=s3_files_deleted,
            pinecone_vectors_deleted=pinecone_vectors_deleted,
            success=success,
            details={
                "s3_operation": "completed" if s3_files_deleted >= 0 else "failed",
                "pinecone_operation": "completed" if pinecone_vectors_deleted >= 0 else "failed",
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
        
    except Exception as e:
        logger.error(f"Critical error during reset operation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reset operation failed: {str(e)}")

