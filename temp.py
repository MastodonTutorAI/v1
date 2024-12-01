import streamlit as st
from streamlit_cookies_controller import CookieController

st.set_page_config('Cookie QuickStart', '🍪', layout='wide')

controller = CookieController()

# Set a cookie
controller.set('cookie_name', 'testing')
st.write(st.session_state)

# Get all cookies
cookies = controller.getAll()
st.write(cookies)

# Get a cookie
cookie = controller.get('cookie_name')
st.write(cookie)

# Remove a cookie
controller.remove('cookie_name')
st.write(st.session_state)