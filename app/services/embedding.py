import logging
from typing import List
from langchain.embeddings.base import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Get logger for this module
logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, model_name: str = None, api_key: str = None):
        """
        Initialize embedding model.
        
        Args:
            provider (str): "google"
            model_name (str): optional model name
            api_key (str): API key for the provider
        """
        try:
            logger.info(f"Initializing embedding model with model_name: {model_name or 'models/embedding-001'}")
            
            # Google Generative AI embeddings
            self.model: Embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name or "models/embedding-001",
                google_api_key=api_key
            )
            logger.debug("Successfully initialized embedding model")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        try:
            logger.debug(f"Embedding query text of length: {len(text)}")
            embedding = self.model.embed_query(text)
            logger.debug(f"Successfully generated query embedding of dimension: {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed query: {str(e)}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        try:
            logger.debug(f"Embedding {len(texts)} documents")
            embeddings = self.model.embed_documents(texts)
            logger.debug(f"Successfully generated embeddings. Shape: {len(embeddings)}x{len(embeddings[0]) if embeddings else 0}")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to embed documents: {str(e)}")
            raise