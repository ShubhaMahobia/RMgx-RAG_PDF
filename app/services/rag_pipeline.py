from typing import Any, Dict, List
import logging
import time
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI  # Example LLM (can be swapped)
import os

# Get logger for this module
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, retriever, llm=None):
        """
        Initialize the RAG pipeline with retriever + LLM.
        
        Args:
            retriever: LangChain retriever (semantic / hybrid / keyword)
            llm: LangChain LLM (defaults to OpenAI, but pluggable)
        """
        logger.info("Initializing RAG Pipeline")
        logger.debug(f"Retriever type: {type(retriever).__name__}")
        
        self.retriever = retriever
        
        if llm:
            logger.debug(f"Using provided LLM: {type(llm).__name__}")
            self.llm = llm
        else:
            logger.info("Initializing default Google Generative AI LLM")
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
            logger.debug(f"LLM initialized: {type(self.llm).__name__}")

        # Define a custom prompt that encourages citations
        logger.debug("Setting up custom prompt template with citation instructions")
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
            "You are an AI assistant that answers questions using ONLY the provided context.\n"
            "If the answer is not in the context, say 'I could not find the answer in the documents.'\n\n"
            "Context:\n{context}\n\n"
            "Question:\n{question}\n\n"
            "Instructions:\n"
            "- Be concise and clear.\n"
            "- Do not add information that is not in the context.\n"
            "- When providing information, reference the source document and page number if available.\n"
            "- Format citations as: [Document Name, Page X] or [Document Name] if no page number.\n"
            "- If multiple sources support the same information, mention all relevant sources.\n\n"
            "Final Answer:"
        )
        )

        # Build RetrievalQA chain
        logger.info("Building RetrievalQA chain")
        try:
            self.chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                retriever=self.retriever,
                chain_type="stuff",   # "stuff" = simple concatenation of docs
                chain_type_kwargs={"prompt": self.prompt},
                return_source_documents=True
            )
            logger.info("RAG Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Pipeline: {str(e)}")
            raise

    def ask(self, query: str) -> Dict[str, Any]:
        """
        Query the RAG pipeline.
        
        Args:
            query (str): User's natural language query
        
        Returns:
            dict with 'answer', 'sources', and 'citations'
        """
        start_time = time.time()
        logger.info(f"Processing query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        try:
            logger.debug("Executing RAG chain")
            response = self.chain(query)
            logger.debug("RAG chain execution completed")

            answer = response["result"]
            sources: List[Document] = response.get("source_documents", [])
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            logger.info(f"Generated answer of length: {len(answer)}")
            logger.info(f"Found {len(sources)} source documents")
            logger.info(f"Processing time: {processing_time:.2f}ms")
            
            # Debug: Log metadata structure
            for i, doc in enumerate(sources):
                logger.debug(f"Source {i} metadata keys: {list(doc.metadata.keys())}")
                logger.debug(f"Source {i} metadata: {doc.metadata}")
                logger.debug(f"Source {i} content length: {len(doc.page_content)}")

            # Extract citation metadata
            citations = []
            logger.info(f"Creating citations from {len(sources)} source documents")
            
            for i, doc in enumerate(sources):
                metadata = doc.metadata
                logger.debug(f"Processing source document {i+1}")
                logger.debug(f"Document {i+1} metadata keys: {list(metadata.keys())}")
                
                # Extract PDF name - prioritize pdf_name field, then original_filename, then source
                pdf_name = metadata.get('pdf_name', 'Unknown')
                if not pdf_name or pdf_name == 'Unknown':
                    pdf_name = metadata.get('original_filename', 'Unknown')
                
                if not pdf_name or pdf_name == 'Unknown':
                    # Fallback to source field
                    pdf_name = metadata.get('source', 'Unknown')
                    if pdf_name and '/' in pdf_name:
                        pdf_name = pdf_name.split('/')[-1]
                        # Remove UUID prefix if present
                        if '_' in pdf_name and len(pdf_name.split('_')[0]) == 32:
                            pdf_name = '_'.join(pdf_name.split('_')[1:])
                
                # If still unknown, try to extract from file_path
                if not pdf_name or pdf_name == 'Unknown':
                    file_path = metadata.get('file_path', '')
                    if file_path:
                        pdf_name = os.path.basename(file_path)
                        if '_' in pdf_name and len(pdf_name.split('_')[0]) == 32:
                            pdf_name = '_'.join(pdf_name.split('_')[1:])
                
                # Final fallback
                if not pdf_name or pdf_name == 'Unknown':
                    pdf_name = 'Unknown Document'
                
                logger.debug(f"Document {i+1} PDF name extracted: {pdf_name}")
                
                # Extract page number
                page_number = metadata.get('page', None)
                if page_number is not None:
                    try:
                        page_number = int(page_number)
                    except (ValueError, TypeError):
                        page_number = None
                
                logger.debug(f"Document {i+1} page number: {page_number}")
                
                # Get chunk text (truncate if too long for readability)
                chunk_text = doc.page_content
                if len(chunk_text) > 500:
                    chunk_text = chunk_text[:500] + "..."
                
                citation = {
                    'page_number': page_number,
                    'pdf_name': pdf_name,
                    'chunk_text': chunk_text,
                    'confidence_score': 0.8,  # Default confidence score for trust building
                    'metadata': metadata
                }
                
                citations.append(citation)
                logger.debug(f"Created citation {i+1}: {pdf_name}, page {page_number}, text length: {len(chunk_text)}")
                logger.debug(f"Citation {i+1} structure: {citation}")
            
            logger.info(f"Successfully created {len(citations)} citations")

            return {
                "answer": answer,
                "sources": sources,
                "citations": citations,
                "total_sources": len(sources),
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            raise
