from fastapi import FastAPI
from app.routes import upload
from app.utils.logger import configure_logger
import logging
import os

# Configure logging
configure_logger()

# Get logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF RAG Chatbot")

# Include routes
app.include_router(upload.router, prefix="/api", tags=["Upload"])

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application starting up...")
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
    logger.info(f"Vector store directory: data/chroma")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutting down...")

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "ok"}

