from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from app.services.embedding import EmbeddingModel
from app.services.vectore_store import VectorStoreHandler
from app.services.retriever import RetrieverFactory
from app.services.rag_pipeline import RAGPipeline
import os

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    query: str
    retriever_type: str = "hybrid"  # "semantic" | "keyword" | "hybrid"

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Answer a question using RAG pipeline with semantic/keyword/hybrid retrieval.
    """
    logger.info(f"Processing chat request: {request.query[:100]}{'...' if len(request.query) > 100 else ''}")
    logger.info(f"Retriever type requested: {request.retriever_type}")
    
    try:
        # 1. Load embedding model
        logger.debug("Loading embedding model")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("Google API key not found in environment")
            raise HTTPException(status_code=500, detail="Google API key not configured.")

        embedder = EmbeddingModel(api_key=google_api_key)
        logger.info("Embedding model loaded successfully")

        # 2. Load vectorstore
        logger.debug("Loading vector store")
        vs_handler = VectorStoreHandler(persist_dir="data/chroma")
        vectorstore = vs_handler.load_vectorstore(embedder.model)
        logger.info("Vector store loaded successfully")

        # 3. Create retriever
        logger.debug("Creating retriever")
        retriever_factory = RetrieverFactory(vectorstore)

        if request.retriever_type == "semantic":
            logger.info("Using semantic retriever")
            retriever = retriever_factory.get_semantic_retriever(k=5)
        elif request.retriever_type == "keyword":
            logger.warning("Keyword retriever not supported via API yet")
            raise HTTPException(status_code=400, detail="Keyword retriever not supported via API yet.")
        else:
            # hybrid retriever
            logger.info("Using hybrid retriever (falling back to semantic)")
            # hybrid needs original docs → we can fix later to cache docs after upload
            retriever = retriever_factory.get_semantic_retriever(k=5)

        # 4. Run RAG pipeline
        logger.info("Initializing RAG pipeline")
        rag = RAGPipeline(retriever=retriever)
        
        logger.info("Executing RAG query")
        response = rag.ask(request.query)
        
        logger.info("Chat request processed successfully")
        return {
            "query": request.query,
            "answer": response["answer"],
        }
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
