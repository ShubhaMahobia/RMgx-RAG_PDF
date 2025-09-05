from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import pinecone
import logging
from dotenv import load_dotenv
load_dotenv()
from app.services.pinecone_store import PineconeVectorStoreHandler

from app.services.embedding import EmbeddingModel
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)
router = APIRouter()

# Input schema
class ChatRequest(BaseModel):
    query: str

# Output schema
class ChatResponse(BaseModel):
    answer: str



llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

vs_handler = PineconeVectorStoreHandler()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        query_text = request.query
        logger.info(f"Received chat query: {query_text}")

        # 1. Embed query using your wrapper
        embedder = EmbeddingModel(api_key=os.getenv("GOOGLE_API_KEY"))
        query_embedding = embedder.embed_query(query_text)

        # 2. Search Pinecone for similar docs
        search_results = vs_handler.pc.Index(vs_handler.index_name).query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
            namespace="default"
        )

        if not search_results.matches:
            return ChatResponse(answer="I could not find any relevant information.")

        # 3. Collect retrieved context
        retrieved_contexts = [
            match.metadata.get("text", "")
            for match in search_results.matches
            if "text" in match.metadata
        ]
        context_str = "\n\n".join(retrieved_contexts)

        # 4. Construct RAG prompt
        prompt = f"""
            You are a helpful assistant. 
            Answer the question using the context below. 
            If the answer cannot be found in the context, say "I don't know".

            Context:
            {context_str}

            Question: {query_text}

            Answer:
            """

        # 5. Call LLM with constructed prompt
        response = llm.invoke(prompt)

        return ChatResponse(answer=response.content)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
