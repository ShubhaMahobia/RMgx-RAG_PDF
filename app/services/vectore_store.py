import os
from typing import List, Optional
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings.base import Embeddings

class VectorStoreHandler:
    def __init__(self, persist_dir: str = "data/chroma"):
        """
        Initialize Chroma vector store handler.
        
        Args:
            persist_dir (str): Path to store persistent database.
        """
        self.persist_dir = persist_dir
        self.vectorstore: Optional[Chroma] = None

        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)

    def save_documents(self, documents: List[Document], embedding_model: Embeddings) -> Chroma:
        """
        Save documents into Chroma vector store with embeddings.
        
        Args:
            documents (List[Document]): Chunked documents with metadata
            embedding_model (Embeddings): Embedding model instance
        """
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            persist_directory=self.persist_dir
        )

        # Persist to disk
        self.vectorstore.persist()
        return self.vectorstore

    def load_vectorstore(self, embedding_model: Embeddings) -> Chroma:
        """
        Load existing Chroma vector store from persistence.
        """
        self.vectorstore = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=embedding_model
        )
        return self.vectorstore

    def get_retriever(self, k: int = 5):
        """
        Get retriever interface for querying vectorstore.
        """
        if not self.vectorstore:
            raise RuntimeError("Vectorstore is not initialized. Load or save documents first.")
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
