import os
import shutil
import logging
from from_root import from_root

# Get logger for this module
logger = logging.getLogger(__name__)

def cleanup_all_data():
    """
    Remove all existing PDF files and ChromaDB data for a fresh start.
    This function is called automatically when the application starts.
    """
    logger.info("Starting automatic startup cleanup...")
    
    try:
        # Clean up PDF uploads
        upload_dir = os.path.join(from_root(), "data", "uploads")
        if os.path.exists(upload_dir):
            logger.info(f"Removing PDF uploads directory: {upload_dir}")
            shutil.rmtree(upload_dir)
            logger.info("PDF uploads directory removed successfully")
        else:
            logger.info("PDF uploads directory doesn't exist, skipping...")
        
        # Clean up ChromaDB data
        chroma_dir = os.path.join(from_root(), "data", "chroma")
        if os.path.exists(chroma_dir):
            logger.info(f"Removing ChromaDB directory: {chroma_dir}")
            shutil.rmtree(chroma_dir)
            logger.info("ChromaDB directory removed successfully")
        else:
            logger.info("ChromaDB directory doesn't exist, skipping...")
        
        # Clean up index directory (if exists)
        index_dir = os.path.join(from_root(), "data", "index")
        if os.path.exists(index_dir):
            logger.info(f"Removing index directory: {index_dir}")
            shutil.rmtree(index_dir)
            logger.info("Index directory removed successfully")
        else:
            logger.info("Index directory doesn't exist, skipping...")
        
        logger.info("Automatic startup cleanup completed successfully! All data has been removed.")
        return True
        
    except Exception as e:
        logger.error(f"Error during automatic startup cleanup: {str(e)}")
        raise
