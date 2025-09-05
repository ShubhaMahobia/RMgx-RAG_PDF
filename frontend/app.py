import streamlit as st
import os
from dotenv import load_dotenv
from components.chat_interface import render_chat_interface
from components.file_uploader import render_file_uploader
from components.file_manager import render_file_manager
from api_client import api_client
from config import config

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.SIDEBAR_STATE
)

def main():
    """Main Streamlit application"""

    # Title and description
    st.title("📚 PDF RAG Chatbot")
    st.markdown("""
    Upload PDF documents and chat with them using AI-powered retrieval-augmented generation.
    """)

    # API Configuration in sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API URL Configuration
        current_api_url = st.text_input(
            "API Base URL:",
            value=config.API_BASE_URL,
            help="Configure the backend API URL"
        )

        # Update API client URL if changed
        if current_api_url != api_client.base_url:
            api_client.base_url = current_api_url.rstrip('/')

        # Backend connection status
        try:
            status = api_client.health_check()
            if status.get("status") == "ok":
                st.success("✅ Backend Connected")
            else:
                st.error("❌ Backend Connection Failed")
        except Exception as e:
            st.error(f"❌ Backend Error: {str(e)}")

        st.header("Navigation")

        # Navigation tabs
        tab = st.radio(
            "Choose Action:",
            ["Chat", "Upload PDFs", "Manage Files"],
            label_visibility="collapsed"
        )


    # Main content based on selected tab
    if tab == "Chat":
        render_chat_interface()
    elif tab == "Upload PDFs":
        render_file_uploader()
    elif tab == "Manage Files":
        render_file_manager()

if __name__ == "__main__":
    main()
