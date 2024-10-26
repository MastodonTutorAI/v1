import streamlit as st
from service import service

def init_page():
    if 'service_initialized' not in st.session_state:
        st.session_state.service = service.Service()
        st.session_state.service_initialized = True

    if "selected_course_id" not in st.session_state:
        st.session_state.selected_course_id = None

    # Initialize session state for login status if not already set
    if "isLogined" not in st.session_state:
        st.session_state.isLogined = False

    if "isAdmin" not in st.session_state:
        st.session_state.isAdmin = False

    if 'uploaded_files' not in st.session_state:
        st.session_state['uploaded_files'] = []

    if 'uploader_key' not in st.session_state:
        st.session_state['uploader_key'] = 0
    
    if 'content_page_visibility' not in st.session_state:
        st.session_state['content_page_visibility'] = False
    
    if 'assistant_page_visibility' not in st.session_state:
        st.session_state['assistant_page_visibility'] = False
    
    if 'content_opened' not in st.session_state:
        st.session_state['content_opened'] = False
    
    if 'assistant_opened' not in st.session_state:
        st.session_state['assistant_opened'] = False
    
    if "conversations" not in st.session_state:
        st.session_state.conversations = []

    if "user" not in st.session_state:
        st.session_state.user = None