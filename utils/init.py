import streamlit as st


def init_page():
    # Initialize session state for login status if not already set
    if "isLogined" not in st.session_state:
        st.session_state.isLogined = False

    if "isAdmin" not in st.session_state:
        st.session_state.isAdmin = False