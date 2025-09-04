from fastapi import FastAPI
from app.routes import upload

app = FastAPI(title="PDF RAG Chatbot")

# Include routes
app.include_router(upload.router, prefix="/api", tags=["Upload"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
