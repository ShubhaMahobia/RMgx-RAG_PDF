from typing import Any, Dict, List
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI  # Example LLM (can be swapped)

class RAGPipeline:
    def __init__(self, retriever, llm=None):
        """
        Initialize the RAG pipeline with retriever + LLM.
        
        Args:
            retriever: LangChain retriever (semantic / hybrid / keyword)
            llm: LangChain LLM (defaults to OpenAI, but pluggable)
        """
        self.retriever = retriever
        self.llm = llm or ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # Define a custom prompt
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
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type="stuff",   # "stuff" = simple concatenation of docs
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )

    def ask(self, query: str) -> Dict[str, Any]:
        """
        Query the RAG pipeline.
        
        Args:
            query (str): User's natural language query
        
        Returns:
            dict with 'answer' and 'sources'
        """
        response = self.chain(query)

        answer = response["result"]
        sources: List[Document] = response.get("source_documents", [])

        source_metadata = [
            {"source": doc.metadata.get("source"), "page": doc.metadata.get("page")}
            for doc in sources
        ]

        return {
            "answer": answer,
            "sources": source_metadata
        }
