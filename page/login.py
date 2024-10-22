import streamlit as st
from service import service

if 'service_initialized' not in st.session_state:
    st.session_state.service = service.Service()
    st.session_state.service_initialized = True

service = st.session_state.service

def authenticate_user(username, password):
    """
    Function to authenticate the user by checking the username and password.
    """
    user = service.login(username, password)
    if user:
        print("Logged in.")
        return True, user['user_role']
    return False, None

def login():
    # st.image("assets\Picture1.jpg", caption="")

    with st.container(border=True):
        username = st.text_input("Username", "")
        password = st.text_input("Password", "", type="password")
        if st.button(label='Login'):
            is_authenticated, role = authenticate_user(username, password)
            
            # If authentication is successful, update session state
            if is_authenticated:
                st.session_state.isLogined = True
                st.session_state.isAdmin = (role == "admin")
                st.success("Login successful!")
                st.rerun()  # Rerun the app to reflect login status
            else:
                st.error("Invalid credentials. Please try again.")

login()