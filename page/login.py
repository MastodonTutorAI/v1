import streamlit as st

service = st.session_state.service

def authenticate_user(username, password):
    """
    Function to authenticate the user by checking the username and password.
    """
    user = service.login(username, password)
    if user:
        print("Logged in.")
        st.session_state.user = user
        return True, user['user_role']
    return False, None

@st.fragment
def login():
    m_col0, m_colm1, m_colm2, m_colm3 = st.columns([1.8, 1.5, 0.1, 4])

    m_colm1.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    
    m_colm1.image("assets/pfw.png", caption="")

    m_colm3.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    
    with m_colm3:
        colms1 = st.columns([0.1, 1, 1])
        colms2 = st.columns([0.1, 1, 1])
        
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
