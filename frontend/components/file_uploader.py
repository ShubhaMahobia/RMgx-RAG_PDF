import streamlit as st
from typing import List
from api_client import api_client
from config import config

def validate_file(file) -> bool:
    """Validate uploaded file"""
    # Check file extension
    if not file.name.lower().endswith('.pdf'):
        return False

    # Check file size
    if len(file.getvalue()) > config.MAX_FILE_SIZE:
        return False

    return True

def render_file_uploader():
    """Render the file uploader component"""

    st.header("📤 Upload PDF Documents")

    st.markdown("""
    Upload PDF files to be processed and made available for chat.
    The system will:
    1. Extract text from PDFs
    2. Split content into chunks
    3. Create embeddings
    4. Store in vector database
    """)

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or more PDF files to upload"
    )

    if uploaded_files:
        st.markdown(f"**Selected files:** {len(uploaded_files)}")

        # Validate and display file details
        valid_files = []
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)

            if not validate_file(file):
                if file_size_mb > config.MAX_FILE_SIZE / (1024 * 1024):
                    st.error(f"❌ {file.name}: File too large ({file_size_mb:.1f}MB). Max allowed: {config.MAX_FILE_SIZE/(1024*1024)}MB")
                else:
                    st.error(f"❌ {file.name}: Invalid file type")
            else:
                st.success(f"✅ {file.name}: {file_size_mb:.1f}MB")
                valid_files.append(file)

        # Upload button
        if valid_files and st.button("🚀 Upload Files", type="primary"):
            # Upload files
            with st.spinner("Uploading and processing files..."):
                try:
                    file_bytes = [file.getvalue() for file in valid_files]
                    filenames = [file.name for file in valid_files]

                    response = api_client.upload_files(file_bytes, filenames)

                    st.success("✅ Files uploaded successfully!")
                    st.json(response)

                    # Refresh the page to update file count
                    st.rerun()

                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

        elif not valid_files:
            st.error("No valid files to upload")

    # Display current uploaded files
    st.markdown("---")
    st.markdown("### Currently Uploaded Files")

    try:
        files_response = api_client.get_uploaded_files()
        files = files_response.get("files", [])

        if files:
            st.success(f"📚 {len(files)} file(s) uploaded")
            for file in files:
                filename = file.split('/')[-1] if '/' in file else file
                st.text(f"• {filename}")
        else:
            st.info("No files uploaded yet")

    except Exception as e:
        st.error(f"Failed to fetch uploaded files: {str(e)}")
