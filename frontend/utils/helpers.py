import streamlit as st
from typing import Any, Dict

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return ".1f"
        size_bytes /= 1024.0
    return ".1f"

def display_api_response(response: Dict[str, Any], title: str = "API Response"):
    """Display API response in a formatted way"""
    with st.expander(title):
        st.json(response)

def validate_pdf_file(file) -> bool:
    """Validate if uploaded file is a valid PDF"""
    if file.type != "application/pdf":
        return False

    # Check file signature (PDF files start with %PDF-)
    file_content = file.getvalue()
    if not file_content.startswith(b'%PDF-'):
        return False

    return True
