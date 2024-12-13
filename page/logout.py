import streamlit as st

if st.session_state.isLogined:
    st.session_state.isLogined = False
    st.session_state.isAdmin = False
    st.session_state['content_opened'] = False
    st.session_state['assistant_opened'] = False
    st.session_state['selected_course'] = None
    st.session_state['uploaded_files'] = []
    st.session_state['messages'] = []
    st.session_state['is_system_prompt'] = False
    st.session_state['selected_conversation'] = None
    st.rerun()