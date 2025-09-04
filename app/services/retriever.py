from typing import List
import logging
from langchain.schema import Document
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_chroma import Chroma

# Get logger for this module
logger = logging.getLogger(__name__)

class RetrieverFactory:
    def __init__(self, vectorstore: Chroma):
        """
        Initialize retriever factory with a vectorstore.
        
        Args:
            vectorstore (Chroma): A Chroma vectorstore instance
        """
        logger.info("Initializing RetrieverFactory")
        logger.debug(f"Vectorstore type: {type(vectorstore).__name__}")
        self.vectorstore = vectorstore

    def get_semantic_retriever(self, k: int = 5):
        """
        Create a semantic retriever using vector embeddings.
        
        Args:
            k (int): number of results to retrieve
        """
        logger.info(f"Creating semantic retriever with k={k}")
        try:
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
            logger.debug("Semantic retriever created successfully")
            return retriever
        except Exception as e:
            logger.error(f"Failed to create semantic retriever: {str(e)}")
            raise

    def get_keyword_retriever(self, documents: List[Document]):
        """
        Create a keyword retriever (BM25).
        
        Args:
            documents (List[Document]): original documents (chunked)
        """
        logger.info(f"Creating keyword retriever with {len(documents)} documents")
        try:
            retriever = BM25Retriever.from_documents(documents)
            logger.debug("Keyword retriever created successfully")
            return retriever
        except Exception as e:
            logger.error(f"Failed to create keyword retriever: {str(e)}")
            raise

    def get_hybrid_retriever(self, documents: List[Document], k: int = 5, weights=(0.7, 0.3)):
        """
        Create a hybrid retriever (semantic + keyword).
        
        Args:
            documents (List[Document]): original documents (chunked)
            k (int): number of results
            weights (tuple): weights for semantic vs keyword retriever
        """
        logger.info(f"Creating hybrid retriever with k={k}, weights={weights}")
        try:
            semantic_retriever = self.get_semantic_retriever(k=k)
            keyword_retriever = self.get_keyword_retriever(documents)

            hybrid = EnsembleRetriever.from_llms(
                retrievers=[semantic_retriever, keyword_retriever],
                weights=list(weights)
            )
            logger.debug("Hybrid retriever created successfully")
            return hybrid
        except Exception as e:
            logger.error(f"Failed to create hybrid retriever: {str(e)}")
            raise
