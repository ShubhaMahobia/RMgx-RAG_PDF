from typing import Optional

class Config:
    APP_NAME = "Demo FastAPI Application"
    VERSION = "1.0.0"
    
    # Embedding Configuration
    EMBEDDING_MODEL = "google"  # can be changed to other models
    GOOGLE_API_KEY: Optional[str] = None  # Set this via environment variable
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIR = "data/index"
    COLLECTION_NAME = "pdf_collection"
    
    # Embedding Dimensions
    EMBEDDING_DIMENSION = 768  # Google's embedding dimension
    
    # Document Processing Configuration
    CHUNK_SIZE = 1000  # Default chunk size in characters
    CHUNK_OVERLAP = 200  # Default chunk overlap in characters