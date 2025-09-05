import streamlit as st
import os
import datetime
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

        # Chat Session Management (only show when in Chat tab)
        if tab == "Chat":
            st.header("💬 Chat Sessions")

            # Initialize chat sessions if not exists
            if "chat_sessions" not in st.session_state:
                st.session_state.chat_sessions = {}
                if "current_session_id" not in st.session_state:
                    st.session_state.current_session_id = "default"
                if st.session_state.current_session_id not in st.session_state.chat_sessions:
                    st.session_state.chat_sessions[st.session_state.current_session_id] = {
                        "messages": [],
                        "name": "Chat 1",
                        "created": datetime.datetime.now()
                    }

            # Display current sessions
            session_keys = list(st.session_state.chat_sessions.keys())
            for session_id in session_keys:
                session_data = st.session_state.chat_sessions[session_id]
                is_current = session_id == st.session_state.current_session_id

                # Enhanced tab styling with better highlighting
                if is_current:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 10px 15px;
                        border-radius: 8px;
                        margin: 2px 0;
                        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                        border: 2px solid #5a67d8;
                        font-weight: bold;
                    ">
                        📌 {session_data['name']}
                    </div>
                    """, unsafe_allow_html=True)

                    # Invisible button overlay for click handling
                    if st.button(
                        session_data['name'],
                        key=f"sidebar_{session_id}",
                        help=f"Current: {session_data['name']}",
                        use_container_width=True
                    ):
                        pass  # Already selected

                    # Delete button for current session (if multiple exist)
                    if len(session_keys) > 1:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("🗑️ Delete", key=f"sidebar_delete_{session_id}", help=f"Delete {session_data['name']}", use_container_width=True):
                                del st.session_state.chat_sessions[session_id]
                                # Switch to another session if current was deleted
                                if session_id == st.session_state.current_session_id:
                                    remaining_sessions = list(st.session_state.chat_sessions.keys())
                                    st.session_state.current_session_id = remaining_sessions[0] if remaining_sessions else "default"
                                st.rerun()
                else:
                    # Inactive tabs with simpler styling
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(
                            session_data['name'],
                            key=f"sidebar_{session_id}",
                            use_container_width=True,
                            help=f"Switch to {session_data['name']}"
                        ):
                            st.session_state.current_session_id = session_id
                            st.rerun()

                    with col2:
                        # Delete button (only show if not the only session)
                        if len(session_keys) > 1:
                            if st.button("❌", key=f"sidebar_delete_{session_id}", help=f"Delete {session_data['name']}"):
                                del st.session_state.chat_sessions[session_id]
                                st.rerun()

            # New Chat button
            if st.button("➕ New Chat", key="sidebar_new_chat", use_container_width=True):
                new_session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                chat_number = len(st.session_state.chat_sessions) + 1
                chat_name = f"Chat {chat_number}"

                st.session_state.chat_sessions[new_session_id] = {
                    "messages": [],
                    "name": chat_name,
                    "created": datetime.datetime.now()
                }
                st.session_state.current_session_id = new_session_id
                st.rerun()


    # Main content based on selected tab
    if tab == "Chat":
        render_chat_interface()
    elif tab == "Upload PDFs":
        render_file_uploader()
    elif tab == "Manage Files":
        render_file_manager()

if __name__ == "__main__":
    main()
