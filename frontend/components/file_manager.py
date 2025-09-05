import streamlit as st
from api_client import api_client

def render_file_manager():
    """Render the file management component"""

    st.header("📁 Manage Uploaded Files")

    # Get uploaded files
    try:
        files_response = api_client.get_uploaded_files()
        files = files_response.get("files", [])

        if not files:
            st.info("No files uploaded yet. Go to 'Upload PDFs' to add files.")
            return

        st.success(f"📚 {len(files)} file(s) uploaded")

        # Display files with delete option
        st.markdown("### Uploaded Files")

        for file_key in files:
            col1, col2 = st.columns([4, 1])

            with col1:
                filename = file_key.split('/')[-1] if '/' in file_key else file_key
                st.write(f"📄 {filename}")

            with col2:
                if st.button(f"🗑️ Delete", key=f"delete_{file_key}"):
                    try:
                        with st.spinner("Deleting file..."):
                            response = api_client.delete_file(file_key)

                        if response.get("success"):
                            st.success(f"✅ {response.get('deleted_file', filename)} deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete file")

                    except Exception as e:
                        st.error(f"Delete failed: {str(e)}")

        # Reset all data option
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")

        with st.expander("Reset Entire Index"):
            st.warning("""
            This will permanently delete ALL uploaded files and their associated data.
            This action cannot be undone!
            """)

            confirm_reset = st.checkbox("I understand this will delete all data")

            if st.button("🔥 Reset Everything", type="secondary", disabled=not confirm_reset):
                try:
                    with st.spinner("Resetting index..."):
                        response = api_client.reset_index()

                    if response.get("success"):
                        st.success("✅ Index reset successfully!")
                        st.json(response.get("details", {}))
                        st.rerun()
                    else:
                        st.error("Reset failed with some errors")
                        st.json(response)

                except Exception as e:
                    st.error(f"Reset failed: {str(e)}")

    except Exception as e:
        st.error(f"Failed to load files: {str(e)}")
