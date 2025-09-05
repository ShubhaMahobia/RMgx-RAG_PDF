# 📚 RMgx-RAG_PDF: Advanced PDF RAG Chatbot

A sophisticated Retrieval-Augmented Generation (RAG) system that transforms PDF documents into an intelligent, conversational knowledge base. Built with modern cloud-native architecture, this application enables users to upload PDF documents and engage in natural language conversations to extract insights, answer questions, and explore document content.

## 🌟 Key Features

### 🎯 **Multi-Session Chat Management**
- **Tab-based conversations**: Create and switch between multiple independent chat sessions
- **Session persistence**: Each conversation maintains its own memory and context
- **Advanced session management**: Rename, delete, and organize conversations with ease

### 📄 **Intelligent Document Processing**
- **Advanced PDF parsing**: Handles both text-based and scanned PDF documents
- **Smart text chunking**: Configurable chunking with overlap for optimal context preservation
- **Metadata enrichment**: Comprehensive document metadata tracking and source attribution

### 🔍 **Semantic Search & RAG**
- **Vector-based retrieval**: Google AI-powered embeddings for semantic understanding
- **Context-aware responses**: Generate answers using retrieved document context
- **Source attribution**: Transparent citation of document sources and page references

### ☁️ **Cloud-Native Architecture**
- **Scalable storage**: AWS S3 integration for document storage
- **Vector database**: Pinecone for high-performance similarity search
- **Secure configuration**: AWS Secrets Manager for sensitive data management
- **Containerized deployment**: Docker support for easy scaling and deployment


## 🔧 How Services Work

### 1. **PDF Processing Service** (`app/services/pdf_loader.py`)

**Purpose**: Converts PDF documents into searchable, chunked text segments.

**How it works**:
```python
# Document Processing Pipeline
1. PDF Upload → Temporary file storage
2. PyPDFLoader → Text extraction with metadata
3. RecursiveCharacterTextSplitter → Intelligent chunking
4. Metadata Enhancement → Source tracking and page references
```

**Key Features**:
- **Intelligent chunking**: Uses recursive character splitting with configurable size (500 chars) and overlap (200 chars)
- **Metadata preservation**: Maintains original filename, page numbers, and file paths
- **Error handling**: Robust error handling for corrupted or unsupported PDF formats

### 2. **Embedding Service** (`app/services/embedding.py`)

**Purpose**: Converts text chunks into high-dimensional vector representations for semantic search.

**How it works**:
```python
# Embedding Generation Process
1. Text Input → Google AI Embedding Model (models/embedding-001)
2. Vector Generation → 768-dimensional embeddings
3. Batch Processing → Efficient handling of multiple documents
4. Quality Validation → Embedding dimension verification
```

**Key Features**:
- **Google AI Integration**: Uses Google's state-of-the-art embedding model
- **Task-specific optimization**: Configured for retrieval document task type
- **Batch processing**: Efficient handling of multiple documents simultaneously

### 3. **Vector Store Service** (`app/services/pinecone_store.py`)

**Purpose**: Manages vector storage, indexing, and similarity search operations.

**How it works**:
```python
# Vector Storage Pipeline
1. Document Chunks → Vector Embeddings
2. Pinecone Index → Serverless vector database
3. Namespace Management → Organized data separation
4. Similarity Search → Cosine similarity matching
```

**Key Features**:
- **Serverless architecture**: Auto-scaling Pinecone serverless index
- **Namespace isolation**: Separate data spaces for different document sets
- **High-performance search**: Sub-second similarity search across millions of vectors
- **Automatic indexing**: Dynamic index creation and management

### 4. **Storage Service** (`app/services/storage/s3_storage.py`)

**Purpose**: Manages document storage in AWS S3 with secure, scalable file handling.

**How it works**:
```python
# S3 Storage Pipeline
1. File Upload → Multipart upload with encryption
2. UUID Generation → Unique file identifiers
3. Metadata Storage → Original filename preservation
4. Presigned URLs → Secure file access
```

**Key Features**:
- **Multipart uploads**: Efficient handling of large PDF files
- **Server-side encryption**: AES256 encryption for data security
- **Presigned URLs**: Secure, time-limited file access
- **Bulk operations**: Efficient batch file management

### 5. **Memory Service** (`app/services/memory.py`)

**Purpose**: Manages conversation history and context across chat sessions.

**How it works**:
```python
# Memory Management
1. Session Creation → Unique session identifiers
2. Context Buffer → ConversationBufferWindowMemory (last 5 interactions)
3. Context Retrieval → Historical conversation access
4. Memory Persistence → Session-based memory storage
```

**Key Features**:
- **Session isolation**: Independent memory for each conversation
- **Context window**: Configurable conversation history (5 interactions)
- **Memory efficiency**: Optimized storage of conversation context

### 6. **RAG Pipeline** (`app/routes/chat.py`)

**Purpose**: Orchestrates the complete RAG process from query to response.

**How it works**:
```python
# RAG Processing Pipeline
1. Query Input → User question processing
2. Query Embedding → Convert question to vector
3. Vector Search → Find similar document chunks (top-k=3)
4. Context Assembly → Combine retrieved chunks
5. LLM Generation → Google Gemini 2.0 Flash response
6. Source Attribution → Document and page references
```

**Key Features**:
- **Hybrid approach**: Combines LangChain Runnable and LLMChain for reliability
- **Context filtering**: Similarity score-based relevance filtering
- **Source tracking**: Complete attribution of information sources
- **Fallback handling**: Graceful degradation when no relevant context is found

## 🚀 Technology Stack & Why These Choices

### **Backend Framework: FastAPI**

**Why FastAPI over Flask/Django?**
- **Performance**: 2-3x faster than Flask, comparable to Node.js and Go
- **Type Safety**: Built-in Pydantic integration for automatic data validation
- **Async Support**: Native async/await support for high concurrency
- **Auto Documentation**: Automatic OpenAPI/Swagger documentation generation
- **Modern Python**: Full support for Python 3.8+ features and type hints

**Advantages**:
```python
# Automatic validation and serialization
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # FastAPI automatically validates request and serializes response
```

### **Vector Database: Pinecone**

**Why Pinecone over Chroma/Weaviate?**
- **Serverless Architecture**: No infrastructure management required
- **Global Scale**: Built for production-scale applications
- **Performance**: Sub-100ms query latency even with millions of vectors
- **Managed Service**: Automatic scaling, backups, and monitoring
- **Enterprise Features**: Advanced security, compliance, and support



### **Embedding Model: Google Generative AI**

**Performance Comparison**:
- **Google embedding-001**: 768 dimensions, optimized for retrieval
- **OpenAI text-embedding-3-small**: 1536 dimensions, higher cost
- **Sentence Transformers**: Local models, limited by hardware

### **Frontend: Streamlit**

**Why Streamlit over React/Next.js?**
- **Rapid Development**: Python-based, no JavaScript required
- **Built-in Components**: Pre-built UI components for data applications
- **Session Management**: Built-in state management for multi-session support
- **Deployment**: Simple deployment with minimal configuration
- **Data Science Focus**: Optimized for ML/AI applications

**Advantages for RAG Applications**:
```python
# Built-in session state management
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
```

### **Cloud Services: AWS**

**Why AWS over GCP/Azure?**
- **Maturity**: Most mature cloud platform with extensive services
- **Integration**: Seamless integration between S3, Secrets Manager, and other services
- **Cost Optimization**: Pay-as-you-go pricing with reserved capacity options
- **Global Reach**: Extensive global infrastructure
- **Security**: Enterprise-grade security and compliance features

## 🏛️ Architecture Design Principles

### **1. Modular Architecture**

**Design Pattern**: Service-Oriented Architecture (SOA)
```python
# Each service is independently deployable and testable
class PDFLoader:
    def load(self) -> List[Document]: ...
    def split(self) -> List[Document]: ...

class EmbeddingModel:
    def embed_query(self, text: str) -> List[float]: ...
    def embed_documents(self, texts: List[str]) -> List[List[float]]: ...
```

**Benefits**:
- **Maintainability**: Easy to update individual components
- **Testability**: Each service can be unit tested independently
- **Scalability**: Services can be scaled independently based on demand

### **2. Cloud-Native Design**

**Design Pattern**: Twelve-Factor App Methodology
- **Configuration**: Environment-based configuration management
- **Stateless**: Stateless services for horizontal scaling
- **Logs**: Centralized logging with structured log format
- **Dependencies**: Explicit dependency declaration

**Implementation**:
```python
# Environment-based configuration
class Config:
    PINECONE_API_KEY: Optional[str] = None  # From environment
    GOOGLE_API_KEY: Optional[str] = None    # From environment
    S3_BUCKET_NAME: str = "my-rag-bucket"   # Configurable
```

### **3. Event-Driven Architecture**

**Design Pattern**: Asynchronous Processing
```python
# Async endpoints for better concurrency
@router.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    # Non-blocking file processing
    for file in files:
        await process_file_async(file)
```

**Benefits**:
- **Concurrency**: Handle multiple requests simultaneously
- **Resource Efficiency**: Better CPU and memory utilization
- **User Experience**: Non-blocking operations

### **4. Fault Tolerance**

**Design Pattern**: Circuit Breaker and Retry Logic
```python
# Graceful error handling
try:
    response = chain.invoke(query_text)
except Exception as chain_error:
    # Fallback to alternative approach
    logger.warning(f"Chain failed: {chain_error}, using fallback")
    response = fallback_chain.run(context=context_str, question=query_text)
```

**Features**:
- **Graceful Degradation**: System continues to function with reduced capabilities
- **Monitoring**: Comprehensive logging and error tracking


### **Prerequisites**
- Python 3.13+
- AWS Account (for S3 and Secrets Manager)
- Google AI API Key
- Pinecone Account

### **Quick Start**
```bash
# Clone the repository
git clone <repository-url>
cd RMgx-RAG_PDF

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the backend
uvicorn app.main:app --reload

# Start the frontend (in another terminal)
cd frontend
streamlit run app.py
```

### **Docker Deployment**
```bash
# Build and run with Docker
docker build -t rmgx-rag-pdf .
docker run -p 8000:8000 rmgx-rag-pdf
```

