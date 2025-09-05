import os
import logging
from typing import List, Optional
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings.base import Embeddings
from pinecone import Pinecone, ServerlessSpec
from app.config import Config

# Get logger for this module
logger = logging.getLogger(__name__)

class PineconeVectorStoreHandler:
    def __init__(self, index_name: str = None, namespace: str = "default"):
        """
        Initialize Pinecone vector store handler.
        
        Args:
            index_name (str): Name of the Pinecone index
            namespace (str): Namespace within the index
        """
        self.index_name = index_name or Config.PINECONE_INDEX_NAME
        self.namespace = namespace
        self.vectorstore: Optional[PineconeVectorStore] = None
        
        # Initialize Pinecone client
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY environment variable not set")
        
        logger.info(f"Initializing PineconeVectorStoreHandler with index: {self.index_name}, namespace: {self.namespace}")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=api_key)
        # Check if index exists, create if not
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if it doesn't."""
        try:
            # List existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                # Create index with serverless spec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=Config.EMBEDDING_DIMENSION,  # Google embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info(f"Pinecone index '{self.index_name}' created successfully")
            else:
                logger.info(f"Pinecone index '{self.index_name}' already exists")
                
        except Exception as e:
            logger.error(f"Failed to ensure Pinecone index exists: {str(e)}")
            raise

    def save_documents(self, documents: List[Document], embedding_model: Embeddings) -> PineconeVectorStore:
        """
        Save documents into Pinecone vector store with embeddings.
        
        Args:
            documents (List[Document]): Chunked documents with metadata
            embedding_model (Embeddings): Embedding model instance
        """
        try:
            logger.info(f"Saving {len(documents)} documents to Pinecone vector store")
            logger.debug(f"Using embedding model: {type(embedding_model).__name__}")
            
            # Log metadata information for debugging
            for i, doc in enumerate(documents[:3]):  # Log first 3 documents
                logger.debug(f"Document {i} metadata: {doc.metadata}")
            
            # Get the index
            index = self.pc.Index(self.index_name)
            
            # Create Pinecone vector store
            self.vectorstore = PineconeVectorStore(
                index=index,
                embedding=embedding_model,
                namespace=self.namespace
            )
            
            # Add documents to the vector store
            self.vectorstore.add_documents(documents)
            
            logger.info("Documents saved to Pinecone vector store successfully")
            return self.vectorstore
            
        except Exception as e:
            logger.error(f"Failed to save documents to Pinecone vector store: {str(e)}")
            raise

    def load_vectorstore(self, embedding_model: Embeddings) -> PineconeVectorStore:
        """
        Load existing Pinecone vector store.
        """
        try:
            logger.info("Loading existing Pinecone vector store")
            logger.debug(f"Using embedding model: {type(embedding_model).__name__}")
            
            # Get the index
            index = self.pc.Index(self.index_name)
            
            # Create Pinecone vector store
            self.vectorstore = PineconeVectorStore(
                index=index,
                embedding=embedding_model,
                namespace=self.namespace
            )
            
            logger.info("Pinecone vector store loaded successfully")
            return self.vectorstore
            
        except Exception as e:
            logger.error(f"Failed to load Pinecone vector store: {str(e)}")
            raise

    def get_retriever(self, k: int = 3):
        """
        Get retriever interface for querying vectorstore.
        """
        if not self.vectorstore:
            logger.error("Vectorstore is not initialized. Load or save documents first.")
            raise RuntimeError("Vectorstore is not initialized. Load or save documents first.")
        
        logger.debug(f"Creating retriever with k={k} documents")
        return self.vectorstore.as_retriever(
            search_kwargs={
                "k": k,
                "score_threshold": 0.0,
                "include_metadata": True
            }
        )
    
    def test_similarity_search(self, query: str, k: int = 3):
        """
        Test similarity search directly on the vectorstore.
        """
        if not self.vectorstore:
            logger.error("Vectorstore is not initialized.")
            raise RuntimeError("Vectorstore is not initialized.")
        
        try:
            logger.debug(f"Testing similarity search with query: {query}")
            docs = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Similarity search returned {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            raise

    def delete_all(self):
        """
        Delete all vectors from the namespace.
        """
        try:
            if not self.vectorstore:
                logger.error("Vectorstore is not initialized.")
                raise RuntimeError("Vectorstore is not initialized.")
            
            logger.info(f"Deleting all vectors from namespace: {self.namespace}")
            self.vectorstore.delete(delete_all=True)
            logger.info("All vectors deleted successfully")
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {str(e)}")
            raise

    def get_stats(self):
        """
        Get statistics about the vector store.
        """
        try:
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            logger.info(f"Pinecone index stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {str(e)}")
            raise

    
    def delete_all_vectors(self):
        """
        Delete all vectors from the Pinecone index.
        
        Returns:
            int: Number of vectors deleted
        """
        try:
            index = self.pc.Index(self.index_name)
            
            logger.info("Starting bulk deletion of all vectors from Pinecone")
            
            # Get current stats to know how many vectors we're deleting
            stats = index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            
            if total_vectors == 0:
                logger.info("No vectors found in Pinecone index")
                return 0
            
            logger.info(f"Found {total_vectors} vectors to delete from Pinecone")
            
            # Delete all vectors in the namespace
            index.delete(delete_all=True, namespace=self.namespace)
            
            logger.info(f"Successfully deleted all {total_vectors} vectors from Pinecone")
            return total_vectors
            
        except Exception as e:
            logger.error(f"Failed to delete all vectors from Pinecone: {str(e)}")
            raise

    def save_vectors(self, chunks, embeddings):
        ids = [f"{chunk.metadata['file_name']}_{chunk.metadata['chunk_id']}" for chunk in chunks]
        meta = []

        for i, chunk in enumerate(chunks):
            metadata = chunk.metadata.copy()
            metadata["text"] = chunk.page_content  
            meta.append(metadata)

        # upsert into Pinecone
        self.pc.Index(self.index_name).upsert(
            vectors=[(ids[i], embeddings[i], meta[i]) for i in range(len(chunks))],
            namespace="default"
        )
        print(f"✅ Saved {len(chunks)} vectors to Pinecone")

