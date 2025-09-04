from typing import Any, Dict, List
import logging
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI  # Example LLM (can be swapped)

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

        # Define a custom prompt
        logger.debug("Setting up custom prompt template")
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
            "- If relevant, include the source (document name and page number).\n\n"
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
            dict with 'answer' and 'sources'
        """
        logger.info(f"Processing query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        try:
            logger.debug("Executing RAG chain")
            response = self.chain(query)
            logger.debug("RAG chain execution completed")

            answer = response["result"]
            sources: List[Document] = response.get("source_documents", [])
            
            logger.info(f"Generated answer of length: {len(answer)}")
            logger.info(f"Found {len(sources)} source documents")

            source_metadata = [
                {"source": doc.metadata.get("source"), "page": doc.metadata.get("page")}
                for doc in sources
            ]
            
            logger.debug(f"Source metadata: {source_metadata}")

            return {
                "answer": answer,
                "sources": source_metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            raise
