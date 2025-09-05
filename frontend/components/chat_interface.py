import streamlit as st
from typing import Dict, Any
from api_client import api_client
from config import config

def render_chat_interface():
    """Render the chat interface component"""

    st.header("💬 Chat with Your PDFs")

    # Check if there are uploaded files
    try:
        files_response = api_client.get_uploaded_files()
        total_files = files_response.get("total_files", 0)

        if total_files == 0:
            st.warning("⚠️ No PDF files uploaded yet. Please upload some PDFs first in the 'Upload PDFs' tab.")
            return
        else:
            st.success(f"📚 {total_files} PDF(s) available for chat")
    except Exception as e:
        st.error(f"Failed to check uploaded files: {str(e)}")
        return

    # Chat interface
    col1, col2 = st.columns([4, 1])

    with col1:
        query = st.text_input(
            "Ask a question about your documents:",
            placeholder="What would you like to know?",
            key="chat_query"
        )

    with col2:
        st.write("")
        ask_button = st.button("Ask", type="primary", use_container_width=True)

    # Process chat query
    if ask_button and query.strip():
        with st.spinner("Thinking..."):
            try:
                response = api_client.chat(query.strip())

                # Display answer
                st.markdown("### Answer:")
                answer = response.get("answer", "No answer received")
                st.write(answer)

                # Display sources
                sources = response.get("sources", [])
                if sources:
                    st.markdown("### 📚 Sources:")

                    # Create a container for better layout
                    with st.container():
                        for i, source in enumerate(sources[:config.MAX_SOURCES_DISPLAY], 1):
                            # Create columns for better spacing
                            col1, col2 = st.columns([1, 4])

                            with col1:
                                st.markdown(f"**Source {i}**")
                                st.caption(f"📄 {source['pdf_name']}")

                            with col2:
                                with st.expander(f"Page {source.get('page_number', 'N/A')}", expanded=False):
                                    # Better formatted text display
                                    relevant_text = source.get('relevant_text', '')
                                    if relevant_text:
                                        # Use markdown for better text formatting
                                        st.markdown(f"""
                                        <div style='
                                            background-color: #f8f9fa;
                                            padding: 15px;
                                            border-radius: 8px;
                                            border-left: 4px solid #007bff;
                                            margin: 5px 0;
                                            line-height: 1.6;
                                            text-align: justify;
                                        '>
                                            {relevant_text}
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.info("No relevant text available")
                else:
                    st.info("No specific sources found for this query.")

                # Store in session state for history
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []

                st.session_state.chat_history.append({
                    "query": query.strip(),
                    "answer": answer,
                    "sources": sources
                })

                # Keep only recent history
                st.session_state.chat_history = st.session_state.chat_history[-config.MAX_CHAT_HISTORY:]

            except Exception as e:
                st.error(f"Chat failed: {str(e)}")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### Chat History")

        for i, chat_item in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.expander(f"Q: {chat_item['query'][:50]}{'...' if len(chat_item['query']) > 50 else ''}"):
                st.write(f"**Question:** {chat_item['query']}")
                st.write(f"**Answer:** {chat_item['answer']}")

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
