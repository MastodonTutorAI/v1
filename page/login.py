import streamlit as st

def login():
    # st.image("assets\Picture1.jpg", caption="")

    with st.container(border=True):
        username = st.text_input("Username", "admin")
        password = st.text_input("Password", "admin", type="password")
        if st.button(label='Login', type='primary'):
            # Perform login check (e.g., validate credentials)
            if username == "admin" and password == "admin":
                st.session_state.isLogined = True
                st.session_state.isAdmin = True
                st.success("Login successful!")
                st.rerun()
            elif username == "student" and password == "student":
                st.session_state.isLogined = True
                st.session_state.isAdmin = False
                st.success("Login successful!")
                st.rerun()

login()