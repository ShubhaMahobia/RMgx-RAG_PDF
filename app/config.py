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
    
    # Pinecone Configuration
    PINECONE_API_KEY: Optional[str] = None  # Set via environment variable
    PINECONE_ENVIRONMENT = "aped-4627-b74a"  # From your URL
    PINECONE_INDEX_NAME = "rag-assignment-setup"  # From your URL
    PINECONE_HOST = "https://rag-assignment-setup-3kcgbjt.svc.aped-4627-b74a.pinecone.io"
    
    # Embedding Dimensions
    EMBEDDING_DIMENSION = 768  # Google's embedding dimension
    GOOGLE_EMBEDDING_MODEL = "models/embedding-001"
    GOOGLE_LLM_MODEL = "gemini-2.0-flash"

    AWS_DEFAULT_REGION="ap-south-1"
    S3_BUCKET_NAME="my-rag-bucket-assignment"
    S3_UPLOAD_PREFIX= "storage_01"           # where PDFs will go
    S3_CHROMA_PREFIX= "chroma/"  
    
    # Document Processing Configuration
    CHUNK_SIZE = 500  # Default chunk size in characters
    CHUNK_OVERLAP = 200  # Default chunk overlap in characters