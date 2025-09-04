from fastapi import APIRouter, HTTPException
import logging
import time
from app.models.chat import ChatRequest, ChatResponse, Citation
from app.services.embedding import EmbeddingModel
from app.services.vectore_store import VectorStoreHandler
from app.services.retriever import RetrieverFactory
from app.services.rag_pipeline import RAGPipeline
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Answer a question using RAG pipeline with semantic/keyword/hybrid retrieval.
    Returns answer with citations including page numbers and PDF names.
    """
    start_time = time.time()
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
            retriever = retriever_factory.get_semantic_retriever(k=3)
        elif request.retriever_type == "keyword":
            logger.warning("Keyword retriever not supported via API yet")
            raise HTTPException(status_code=400, detail="Keyword retriever not supported via API yet.")
        else:
            # hybrid retriever
            logger.info("Using hybrid retriever (falling back to semantic)")
            # hybrid needs original docs → we can fix later to cache docs after upload
            retriever = retriever_factory.get_semantic_retriever(k=3)

        # 4. Run RAG pipeline
        logger.info("Initializing RAG pipeline")
        rag = RAGPipeline(retriever=retriever)
        
        logger.info("Executing RAG query")
        response = rag.ask(request.query)
        
        # Debug: Log the response structure
        logger.debug(f"RAG response keys: {list(response.keys())}")
        logger.debug(f"Citations data type: {type(response.get('citations'))}")
        if response.get('citations'):
            logger.debug(f"First citation structure: {response['citations'][0] if response['citations'] else 'No citations'}")
        
        # 5. Convert citations to proper format
        citations = []
        logger.info(f"Processing {len(response['citations'])} citations from RAG pipeline")
        
        for i, citation_data in enumerate(response["citations"]):
            logger.debug(f"Processing citation {i+1}: {citation_data}")
            try:
                citation = Citation(
                    page_number=citation_data.get("page_number"),
                    pdf_name=citation_data.get("pdf_name", "Unknown Document"),
                    chunk_text=citation_data.get("chunk_text", ""),
                    confidence_score=citation_data.get("confidence_score", 0.8)
                )
                citations.append(citation)
                logger.debug(f"Successfully created citation {i+1}: {citation.pdf_name}, page {citation.page_number}")
            except Exception as citation_error:
                logger.warning(f"Failed to create citation {i+1} from data: {citation_data}, error: {str(citation_error)}")
                # Create a fallback citation with available data
                try:
                    fallback_citation = Citation(
                        page_number=citation_data.get("page_number"),
                        pdf_name=citation_data.get("pdf_name", "Unknown Document"),
                        chunk_text=citation_data.get("chunk_text", ""),
                        confidence_score=0.8
                    )
                    citations.append(fallback_citation)
                    logger.info(f"Created fallback citation {i+1}: {fallback_citation.pdf_name}")
                except Exception as fallback_error:
                    logger.error(f"Failed to create fallback citation {i+1}: {str(fallback_error)}")
                    continue
        
        # Calculate total processing time
        total_processing_time = (time.time() - start_time) * 1000
        
        logger.info("Chat request processed successfully")
        logger.info(f"Total processing time: {total_processing_time:.2f}ms")
        logger.info(f"Generated {len(citations)} citations")
        
        return ChatResponse(
            query=request.query,
            answer=response["answer"],
            citations=citations,
            total_sources=response["total_sources"],
            processing_time_ms=total_processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
