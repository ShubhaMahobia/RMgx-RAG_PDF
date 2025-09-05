import streamlit as st
from typing import Dict, Any, List
from api_client import api_client
from config import config
from datetime import datetime

def render_chat_interface():
    """Render a modern WhatsApp/ChatGPT-style chat interface with navigation"""

    # Initialize typing state
    if "is_typing" not in st.session_state:
        st.session_state.is_typing = False

    # Check if there are uploaded files
    try:
        files_response = api_client.get_uploaded_files()
        total_files = files_response.get("total_files", 0)
        has_files = total_files > 0
    except Exception as e:
        st.error(f"Failed to check uploaded files: {str(e)}")
        has_files = False



    # Show current chat name in a subtle way
    current_session = st.session_state.chat_sessions[st.session_state.current_session_id]
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 8px;
        margin-bottom: 10px;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e9ecef;
        font-size: 0.9em;
        color: #6c757d;
    ">
        💬 <strong>{current_session['name']}</strong> • {total_files} PDF{'' if total_files == 1 else 's'} available
    </div>
    """, unsafe_allow_html=True)

    if not has_files:
        st.markdown("""
        <div style="
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        ">
            <h3 style="color: #856404; margin-top: 0;">📚 No PDFs Uploaded Yet</h3>
            <p style="color: #856404; margin-bottom: 0;">Please upload some PDF documents first in the "Upload PDFs" tab to start chatting.</p>
        </div>
        """, unsafe_allow_html=True)
        return


    # Enhanced Chat Styling
    st.markdown("""
    <style>
        .chat-messages {
            max-height: 70vh;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
            border-radius: 15px;
            margin: 15px 0;
            border: 1px solid #e9ecef;
            scroll-behavior: smooth;
        }
        .message-bubble {
            max-width: 75%;
            padding: 14px 18px;
            border-radius: 20px;
            margin: 6px 0;
            position: relative;
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .user-message {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 6px;
            animation: slideInRight 0.3s ease-out;
        }
        .assistant-message {
            background: #f8f9fa;
            color: #2c3e50;
            border: 1px solid #e9ecef;
            border-bottom-left-radius: 6px;
            animation: slideInLeft 0.3s ease-out;
        }
        .timestamp {
            font-size: 0.7em;
            opacity: 0.6;
            margin-top: 6px;
            font-weight: 500;
        }
        .message-row {
            display: flex;
            align-items: flex-start;
            margin: 12px 0;
        }
        .message-row.user { justify-content: flex-end; }
        .message-row.assistant { justify-content: flex-start; }
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 16px;
            flex-shrink: 0;
        }
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            padding: 14px 18px;
            background: #f8f9fa;
            border-radius: 20px;
            border-bottom-left-radius: 6px;
            font-style: italic;
            color: #666;
            border: 1px solid #e9ecef;
            animation: pulse 1.5s infinite;
        }
        .typing-dots {
            display: inline-flex;
            gap: 4px;
            margin-left: 8px;
        }
        .typing-dots span {
            width: 4px;
            height: 4px;
            background: #666;
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }

        /* Scrollbar styling */
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 10px;
        }
        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
    </style>
    """, unsafe_allow_html=True)

    # Chat Messages Container
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

    chat_container = st.container()

    # Get current conversation messages
    current_messages = st.session_state.chat_sessions[st.session_state.current_session_id]["messages"]

    with chat_container:
        if not current_messages:
            # Welcome message
            st.markdown("""
            <div style="
                text-align: center;
                padding: 60px 30px;
                color: #666;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 15px;
                margin: 20px 0;
                border: 2px solid #dee2e6;
            ">
                <div style="font-size: 4em; margin-bottom: 20px; animation: bounce 2s infinite;">👋</div>
                <h2 style="color: #2c3e50; margin-bottom: 15px; font-weight: 600;">Welcome to PDF Assistant!</h2>
                <p style="font-size: 1.1em; line-height: 1.6; margin-bottom: 20px;">
                    I'm here to help you chat with your PDF documents. Ask me anything about the content you've uploaded!
                </p>
                <div style="font-size: 0.9em; opacity: 0.8;">
                    💡 Try asking: "What are the main topics covered?" or "Summarize the key points"
                </div>
            </div>
            <style>
                @keyframes bounce {
                    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                    40% { transform: translateY(-10px); }
                    60% { transform: translateY(-5px); }
                }
            </style>
            """, unsafe_allow_html=True)
        else:
            # Display messages
            for i, message in enumerate(current_messages):
                timestamp = message.get('timestamp', datetime.now()).strftime("%H:%M")

                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="message-row user">
                        <div style="flex: 1;"></div>
                        <div class="message-bubble user-message">
                            {message['content']}
                            <div class="timestamp">{timestamp}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Assistant message with sources
                    st.markdown(f"""
                    <div class="message-row assistant">
                        <div class="avatar" style="background: linear-gradient(135deg, #10a37f, #0d8a6a); color: white;">🤖</div>
                        <div class="message-bubble assistant-message">
                            {message['content']}
                            <div class="timestamp">{timestamp}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display sources inline
                    if message.get("sources"):
                        sources = message["sources"]
                        for j, source in enumerate(sources[:config.MAX_SOURCES_DISPLAY], 1):
                            with st.expander(f"📄 Source {j}: {source['pdf_name']} (Page {source.get('page_number', 'N/A')})", expanded=False):
                                relevant_text = source.get('relevant_text', '')
                                if relevant_text:
                                    st.markdown(f"""
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 12px;
                                        border-radius: 8px;
                                        border-left: 4px solid #007bff;
                                        margin: 8px 0;
                                        line-height: 1.6;
                                        font-size: 0.9em;
                                    ">
                                        {relevant_text}
                                    </div>
                                    """, unsafe_allow_html=True)

        # Enhanced Typing indicator
        if st.session_state.is_typing:
            st.markdown("""
            <div class="message-row assistant">
                <div class="avatar" style="background: linear-gradient(135deg, #10a37f, #0d8a6a); color: white;">🤖</div>
                <div class="typing-indicator">
                    Assistant is thinking
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Close chat messages container
    st.markdown('</div>', unsafe_allow_html=True)

    # Message Input Area (Fixed at bottom)
    st.markdown("""
    <style>
        .message-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 20px;
            border-top: 1px solid #e9ecef;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        .message-input {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .message-textarea {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 16px;
            resize: none;
            outline: none;
            transition: border-color 0.3s;
        }
        .message-textarea:focus {
            border-color: #007bff;
        }
        .send-button {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            border: none;
            border-radius: 50%;
            width: 48px;
            height: 48px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            transition: transform 0.2s;
        }
        .send-button:hover {
            transform: scale(1.05);
        }
    </style>
    """, unsafe_allow_html=True)

    # Input form
    with st.form(key="message_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])

        with col1:
            query = st.text_input(
                "Type your message...",
                placeholder="Ask me anything about your PDFs...",
                key="chat_query",
                label_visibility="collapsed"
            )

        with col2:
            submitted = st.form_submit_button("📤", type="primary")

        if submitted and query.strip():
            # Set typing indicator
            st.session_state.is_typing = True

            # Add user message to current session
            user_message = {
                "role": "user",
                "content": query.strip(),
                "timestamp": datetime.now()
            }
            st.session_state.chat_sessions[st.session_state.current_session_id]["messages"].append(user_message)

            try:
                # Send query with session ID
                response = api_client.chat(query.strip(), st.session_state.current_session_id)

                # Get assistant response
                answer = response.get("answer", "No answer received")
                sources = response.get("sources", [])

                # Add assistant message
                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "timestamp": datetime.now()
                }
                st.session_state.chat_sessions[st.session_state.current_session_id]["messages"].append(assistant_message)

            except Exception as e:
                st.error(f"Chat failed: {str(e)}")
                # Remove user message if failed
                current_messages = st.session_state.chat_sessions[st.session_state.current_session_id]["messages"]
                if current_messages and current_messages[-1]["role"] == "user":
                    current_messages.pop()

            # Clear typing indicator
            st.session_state.is_typing = False
            st.rerun()

    # Add some bottom spacing for fixed input
    current_messages = st.session_state.chat_sessions[st.session_state.current_session_id]["messages"]
    if current_messages:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
