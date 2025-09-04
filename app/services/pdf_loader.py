import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Get logger for this module
logger = logging.getLogger(__name__)

class PDFLoader:
    """
    Class to handle PDF loading and document splitting.
    """

    def __init__(self, file_path: str):
        """
        Initialize with the path to the PDF file.
        """
        logger.info(f"Initializing PDFLoader with file path: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not file_path.lower().endswith('.pdf'):
            logger.warning(f"File {file_path} does not have .pdf extension")
            
        self.file_path = file_path
        self.documents: List[Document] = []
        logger.debug(f"PDFLoader initialized successfully for: {file_path}")

    def load(self) -> List[Document]:
        """
        Load PDF file using LangChain's PyPDFLoader.
        Returns a list of Document objects with page text + metadata.
        """
        try:
            logger.info(f"Loading PDF file: {self.file_path}")
            loader = PyPDFLoader(self.file_path)
            self.documents = loader.load()
            logger.info(f"Successfully loaded {len(self.documents)} pages from PDF")
            return self.documents
        except Exception as e:
            logger.error(f"Failed to load PDF file {self.file_path}: {str(e)}")
            raise

    def split(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[Document]:
        """
        Split loaded documents into smaller chunks for embeddings.

        Args:
            chunk_size (int): Max characters per chunk.
            chunk_overlap (int): Overlap between chunks.

        Returns:
            List[Document]: List of chunked Document objects.
        """
        if not self.documents:
            logger.error("No documents loaded. Call load() first.")
            raise ValueError("No documents loaded. Call load() first.")

        try:
            logger.info(f"Splitting {len(self.documents)} documents into chunks")
            logger.debug(f"Chunk size: {chunk_size}, Chunk overlap: {chunk_overlap}")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ".", " ", ""]
            )

            split_docs = text_splitter.split_documents(self.documents)
            logger.info(f"Successfully split documents into {len(split_docs)} chunks")
            return split_docs
        except Exception as e:
            logger.error(f"Failed to split documents: {str(e)}")
            raise
