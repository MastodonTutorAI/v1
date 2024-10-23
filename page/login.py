import streamlit as st

users_db = {
    "admin": {"username": "admin", "password": "admin", "role": "admin"},
    "student": {"username": "student", "password": "student", "role": "student"}
}

def authenticate_user(username, password):
    """
    Function to authenticate the user by checking the username and password.
    In the future, this can be replaced by a database query.
    """
    if username in users_db:
        user = users_db[username]
        if user['password'] == password:
            return True, user['role']
    return False, None

def login():
    # st.image("assets\Picture1.jpg", caption="")
    colms1 = st.columns([1, 1, 1])
    colms2 = st.columns([1, 1, 1])
    
    colms1[1].title("Mastodon TutorAI")
    container = colms2[1].container(border=True)
    with container:
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