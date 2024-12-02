import streamlit as st

if st.session_state.isLogined:
    st.session_state.isLogined = False
    st.session_state.isAdmin = False
    st.rerun()