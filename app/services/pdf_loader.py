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
            documents = loader.load()
            
            # Enhance metadata with original filename and better source tracking
            enhanced_documents = []
            for doc in documents:
                # Extract original filename (not UUID)
                original_filename = os.path.basename(self.file_path)
                logger.debug(f"Original file path: {self.file_path}")
                logger.debug(f"Extracted filename: {original_filename}")
                
                if '_' in original_filename and len(original_filename.split('_')[0]) == 32:
                    # Remove UUID prefix if present
                    original_filename = '_'.join(original_filename.split('_')[1:])
                    logger.debug(f"Removed UUID prefix, new filename: {original_filename}")
                
                # Enhance metadata
                enhanced_metadata = doc.metadata.copy()
                enhanced_metadata.update({
                    'original_filename': original_filename,
                    'file_path': self.file_path,
                    'file_size': os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0,
                    'loader_type': 'PyPDFLoader',
                    'source': original_filename,  # Set source to original filename for citations
                    'pdf_name': original_filename  # Add explicit pdf_name field
                })
                
                logger.debug(f"Enhanced metadata for document: {enhanced_metadata}")
                
                # Create enhanced document
                enhanced_doc = Document(
                    page_content=doc.page_content,
                    metadata=enhanced_metadata
                )
                enhanced_documents.append(enhanced_doc)
            
            self.documents = enhanced_documents
            logger.info(f"Successfully loaded {len(self.documents)} pages from PDF")
            logger.info(f"Original filename: {original_filename}")
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
            
            # Preserve enhanced metadata in split documents
            for doc in split_docs:
                # Ensure the source field points to the original file path for vector store
                if 'file_path' in doc.metadata:
                    doc.metadata['source'] = doc.metadata['file_path']
            
            logger.info(f"Successfully split documents into {len(split_docs)} chunks")
            return split_docs
            
        except Exception as e:
            logger.error(f"Failed to split documents: {str(e)}")
            raise
