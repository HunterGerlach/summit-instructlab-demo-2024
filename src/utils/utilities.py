import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import tempfile

class Utilities:    
    def read_pdf(file):
        import PyPDF2
        reader = PyPDF2.PdfReader(file)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n".join(text)

    def read_text(file):
        return file.getvalue().decode("utf-8")

    def read_docx(file):
        import docx
        doc = docx.Document(file)
        text = [paragraph.text for paragraph in doc.paragraphs]
        return "\n".join(text)
    

    # @staticmethod
    # def attempt_pdf_upload(upload_handler):
    #     """Upload a PDF and return file and content if successful, or None otherwise."""
    #     pdf_file, content = upload_handler()
    #     if not pdf_file:
    #         st.info("Upload a PDF file to get started", icon="👈")
    #         return None, None
    #     return pdf_file, content

    # @staticmethod
    # def handle_upload():
    #     """
    #     Handles the file upload and displays the uploaded file
    #     """
    #     uploaded_file = st.sidebar.file_uploader("upload", type="pdf", label_visibility="collapsed")#| st.file_uploader("upload", type="text", label_visibility="collapsed") | st.sidebar.file_uploader("upload", type="docx", label_visibility="collapsed")
    #     doc_content = ""
    #     if uploaded_file is not None:
    #         if uploaded_file.type == "application/pdf":
    #             doc_content = Utilities.read_pdf(uploaded_file)
    #         elif uploaded_file.type == "text/plain":
    #             doc_content = Utilities.read_text(uploaded_file)
    #         elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    #             doc_content = Utilities.read_docx(uploaded_file)
    #     else:
    #         st.sidebar.info(
    #             "Upload a PDF file to get started", icon="👆"
    #         )
    #         st.session_state["reset_chat"] = True
    #     return uploaded_file, doc_content

    @staticmethod
    def handle_file_upload():
        """
        Handles the file upload process, displays the uploaded file,
        and returns the file and its content if successful.
        """
        st.spinner("Uploading file...")
        uploaded_file = st.sidebar.file_uploader("Upload a file", type=['pdf', 'txt', 'docx'], label_visibility="collapsed")
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                doc_content = Utilities.read_pdf(uploaded_file)
            elif uploaded_file.type == "text/plain":
                doc_content = Utilities.read_text(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_content = Utilities.read_docx(uploaded_file)
            return uploaded_file, doc_content
        else:
            st.sidebar.info(
                "Upload a PDF file to get started", icon="👆"
            )
            # st.sidebar.warning("Please upload a file to proceed.")
            return None, None

