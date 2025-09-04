from typing import List
from langchain.schema import Document
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.vectorstores import Chroma

class RetrieverFactory:
    def __init__(self, vectorstore: Chroma):
        """
        Initialize retriever factory with a vectorstore.
        
        Args:
            vectorstore (Chroma): A Chroma vectorstore instance
        """
        self.vectorstore = vectorstore

    def get_semantic_retriever(self, k: int = 5):
        """
        Create a semantic retriever using vector embeddings.
        
        Args:
            k (int): number of results to retrieve
        """
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def get_keyword_retriever(self, documents: List[Document]):
        """
        Create a keyword retriever (BM25).
        
        Args:
            documents (List[Document]): original documents (chunked)
        """
        return BM25Retriever.from_documents(documents)

    def get_hybrid_retriever(self, documents: List[Document], k: int = 5, weights=(0.7, 0.3)):
        """
        Create a hybrid retriever (semantic + keyword).
        
        Args:
            documents (List[Document]): original documents (chunked)
            k (int): number of results
            weights (tuple): weights for semantic vs keyword retriever
        """
        semantic_retriever = self.get_semantic_retriever(k=k)
        keyword_retriever = self.get_keyword_retriever(documents)

        hybrid = EnsembleRetriever(
            retrievers=[semantic_retriever, keyword_retriever],
            weights=list(weights)
        )
        return hybrid
