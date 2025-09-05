import os
from typing import Optional

class Config:
    """Configuration for the PDF RAG Chatbot Frontend"""

    # Frontend Configuration
    PAGE_TITLE = "📚 PDF RAG Chatbot"
    PAGE_ICON = "📚"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"

    # API Configuration
    @property
    def API_BASE_URL(self) -> str:
        """Get the API base URL from environment or use default"""
        return os.getenv("API_BASE_URL", "http://localhost:8000")

    # Request Configuration
    REQUEST_TIMEOUT = 60  # seconds
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = [".pdf"]

    # UI Configuration
    MAX_CHAT_HISTORY = 10
    MAX_SOURCES_DISPLAY = 3

# Global config instance
config = Config()
