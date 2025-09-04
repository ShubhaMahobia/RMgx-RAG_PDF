import os
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFLoader:
    """
    Class to handle PDF loading and document splitting.
    """

    def __init__(self, file_path: str):
        """
        Initialize with the path to the PDF file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        self.file_path = file_path
        self.documents: List[Document] = []

    def load(self) -> List[Document]:
        """
        Load PDF file using LangChain's PyPDFLoader.
        Returns a list of Document objects with page text + metadata.
        """
        loader = PyPDFLoader(self.file_path)
        self.documents = loader.load()
        return self.documents

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
            raise ValueError("No documents loaded. Call load() first.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        split_docs = text_splitter.split_documents(self.documents)
        return split_docs
