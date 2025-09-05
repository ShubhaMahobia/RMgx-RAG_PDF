import requests
import streamlit as st
from typing import List, Dict, Any, Optional
from config import config

class APIClient:
    """Client for communicating with the PDF RAG backend API"""

    def __init__(self):
        self.base_url = config.API_BASE_URL.rstrip('/')
        self.timeout = config.REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PDF-RAG-Frontend/1.0'
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend API"""
        url = f"{self.base_url}{endpoint}"

        # Set default timeout if not provided
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Request failed: {str(e)}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """Check backend health"""
        return self._make_request("GET", "/health")

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return self._make_request("GET", "/status")

    def upload_files(self, files: List[bytes], filenames: List[str]) -> Dict[str, Any]:
        """Upload PDF files to backend"""
        files_data = []
        for file_bytes, filename in zip(files, filenames):
            files_data.append(("files", (filename, file_bytes, "application/pdf")))

        response = self._make_request("POST", "/api/upload", files=files_data)
        return response

    def get_uploaded_files(self) -> Dict[str, Any]:
        """Get list of uploaded files"""
        return self._make_request("GET", "/api/files")

    def delete_file(self, s3_key: str) -> Dict[str, Any]:
        """Delete a file by S3 key"""
        data = {"s3_key": s3_key}
        return self._make_request("DELETE", "/api/delete", json=data)

    def reset_index(self) -> Dict[str, Any]:
        """Reset entire index"""
        data = {"confirm": True}
        return self._make_request("POST", "/api/reset", json=data)

    def chat(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Send chat query to backend with session ID for memory management"""
        data = {
            "query": query,
            "session_id": session_id
        }
        return self._make_request("POST", "/api/chat", json=data)

    def test_connection(self) -> bool:
        """Test connection to backend"""
        try:
            self.health_check()
            return True
        except:
            return False

# Global API client instance
api_client = APIClient()
