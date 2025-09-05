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
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

logger = logging.getLogger(__name__)
router = APIRouter()

# Input schema
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"  # Session ID for memory management

# Output schema
class Source(BaseModel):
    pdf_name: str
    page_number: int
    relevant_text: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]



llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

vs_handler = PineconeVectorStoreHandler()

# Memory management - store memories by session_id
memory_store = {}

def get_memory(session_id: str):
    """Get or create memory for a session"""
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 interactions
            return_messages=True
        )
    return memory_store[session_id]

# Custom RAG prompt template
RAG_PROMPT = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template="""
    You are a helpful assistant that answers questions based on the provided context from PDF documents.
    Maintain context from the conversation history when relevant.

    Context from documents:
    {context}

    Conversation History:
    {chat_history}

    Current Question: {question}

    Answer based on the context. If the answer cannot be found in the context, say "I don't know based on the available documents".
    """
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        query_text = request.query
        session_id = request.session_id
        logger.info(f"Received chat query: {query_text} for session: {session_id}")

        # Get or create memory for this session
        memory = get_memory(session_id)

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
            # Even with no context, save to memory
            memory.save_context({"input": query_text}, {"output": "I could not find any relevant information in the uploaded documents."})
            return ChatResponse(answer="I could not find any relevant information in the uploaded documents.", sources=[])

        # 3. Collect retrieved context and source information
        retrieved_contexts = []
        sources = []

        # Get similarity scores to filter most relevant matches
        for match in search_results.matches:
            if "text" in match.metadata:
                # Check if the text actually contains relevant information
                text = match.metadata.get("text", "").lower()
                query_keywords = query_text.lower().split()

                # Calculate relevance score based on keyword presence and similarity score
                keyword_matches = sum(1 for keyword in query_keywords if keyword in text)
                if keyword_matches > 0 or match.score > 0.7:  # Only include if keywords match or high similarity
                    retrieved_contexts.append(match.metadata["text"])
                    sources.append(Source(
                        pdf_name=match.metadata.get("file_name", "Unknown"),
                        page_number=match.metadata.get("page_number", None),
                        relevant_text=match.metadata.get("text", None)
                    ))

        # Sort sources by relevance (most relevant first)
        sources = sorted(sources, key=lambda x: len([kw for kw in query_text.lower().split() if kw in x.relevant_text.lower()]), reverse=True)

        # Take only the most relevant source
        sources = sources[:1] if sources else []

        context_str = "\n\n".join(retrieved_contexts)

        # 4. Use LangChain's LLMChain with memory (fallback to older approach if needed)
        try:
            # Try newer Runnable approach first
            chain = (
                {
                    "context": lambda x: context_str,
                    "chat_history": lambda x: memory.buffer_as_str if hasattr(memory, 'buffer_as_str') else "No chat history",
                    "question": RunnablePassthrough()
                }
                | RAG_PROMPT
                | llm
                | StrOutputParser()
            )
            response = chain.invoke(query_text)
        except Exception as chain_error:
            # Fallback to older LLMChain approach
            logger.warning(f"New chain approach failed: {chain_error}, falling back to LLMChain")
            chain = LLMChain(
                llm=llm,
                prompt=RAG_PROMPT,
                memory=memory,
                verbose=False
            )
            response = chain.run(
                context=context_str,
                question=query_text
            )

        return ChatResponse(answer=response, sources=sources)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
