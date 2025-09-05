from fastapi import FastAPI
from app.routes import upload
from app.utils.logger import configure_logger
from app.routes import chat
from app.utils.cleanup import cleanup_all_data
import logging
import os

# Configure logging
configure_logger()

# Get logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF RAG Chatbot")

# Include routes
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up...")
    try:
        logger.info("Performing startup cleanup for fresh instance...")
        cleanup_all_data()
        logger.info("Startup cleanup completed successfully")
    except Exception as e:
        logger.warning(f"Startup cleanup failed: {str(e)}")
    
    logger.info("PDF RAG Chatbot initialized successfully")
    logger.info("Routes loaded and ready to serve")
    logger.info(f"Log files will be saved to: logs/")
    logger.info(f"Log level: DEBUG (file), INFO (console)")
    
    # Log important environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        logger.info("Google API key is configured")
    else:
        logger.warning("Google API key is not configured - embedding features will not work")
    
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Upload directory: data/uploads")
    logger.info(f"Vector store: Pinecone (rag-assignment-setup)")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutting down...")

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "ok"}


@app.get("/")
def welcome():
    logger.debug("Server is running")
    return {"Server": "Running"}

@app.get("/status")
async def status_endpoint():
    """
    Check the current status of data in the system.
    """
    try:
        upload_dir = os.path.join(os.getcwd(), "data", "uploads")
        
        # Check if directories exist and count files
        upload_exists = os.path.exists(upload_dir)
        
        upload_count = 0
        if upload_exists:
            try:
                upload_count = len([f for f in os.listdir(upload_dir) if f.endswith('.pdf')])
            except:
                upload_count = 0
        
        # Check Pinecone connection
        pinecone_status = "unknown"
        try:
            from app.services.pinecone_store import PineconeVectorStoreHandler
            vs_handler = PineconeVectorStoreHandler()
            stats = vs_handler.get_stats()
            pinecone_status = "connected"
            pinecone_vector_count = stats.get('total_vector_count', 0)
        except Exception as e:
            pinecone_status = f"error: {str(e)}"
            pinecone_vector_count = 0
        
        return {
            "status": "success",
            "data_status": {
                "pdf_uploads": {
                    "exists": upload_exists,
                    "count": upload_count,
                    "path": upload_dir
                },
                "pinecone_db": {
                    "status": pinecone_status,
                    "vector_count": pinecone_vector_count,
                    "index_name": "rag-assignment-setup"
                }
            },
            "message": "Data status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {
            "status": "error",
            "message": "Status check failed",
            "details": str(e)
        }



