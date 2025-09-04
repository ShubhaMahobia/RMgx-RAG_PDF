import os
import logging
from typing import List, Optional
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings

# Get logger for this module
logger = logging.getLogger(__name__)

class VectorStoreHandler:
    def __init__(self, persist_dir: str = "data/chroma"):
        """
        Initialize Chroma vector store handler.
        
        Args:
            persist_dir (str): Path to store persistent database.
        """
        logger.info(f"Initializing VectorStoreHandler with persist directory: {persist_dir}")
        self.persist_dir = persist_dir
        self.vectorstore: Optional[Chroma] = None

        if not os.path.exists(self.persist_dir):
            logger.debug(f"Creating persist directory: {self.persist_dir}")
            os.makedirs(self.persist_dir)
        else:
            logger.debug(f"Using existing persist directory: {self.persist_dir}")

    def save_documents(self, documents: List[Document], embedding_model: Embeddings) -> Chroma:
        """
        Save documents into Chroma vector store with embeddings.
        
        Args:
            documents (List[Document]): Chunked documents with metadata
            embedding_model (Embeddings): Embedding model instance
        """
        try:
            logger.info(f"Saving {len(documents)} documents to vector store")
            logger.debug(f"Using embedding model: {type(embedding_model).__name__}")
            
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embedding_model,
                persist_directory=self.persist_dir
            )

            # Persist to disk
            logger.debug("Persisting vector store to disk")
            self.vectorstore.persist()
            
            logger.info("Documents saved to vector store successfully")
            return self.vectorstore
            
        except Exception as e:
            logger.error(f"Failed to save documents to vector store: {str(e)}")
            raise

    def load_vectorstore(self, embedding_model: Embeddings) -> Chroma:
        """
        Load existing Chroma vector store from persistence.
        """
        try:
            logger.info("Loading existing vector store from persistence")
            logger.debug(f"Using embedding model: {type(embedding_model).__name__}")
            
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=embedding_model
            )
            
            logger.info("Vector store loaded successfully from persistence")
            return self.vectorstore
            
        except Exception as e:
            logger.error(f"Failed to load vector store from persistence: {str(e)}")
            raise

    def get_retriever(self, k: int = 3):
        """
        Get retriever interface for querying vectorstore.
        """
        if not self.vectorstore:
            logger.error("Vectorstore is not initialized. Load or save documents first.")
            raise RuntimeError("Vectorstore is not initialized. Load or save documents first.")
        
        logger.debug(f"Creating retriever with k={k} documents")
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
