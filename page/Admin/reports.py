import streamlit as st

service = st.session_state.service

if st.session_state['assistant_opened'] == True:
    #Save Conversations
    service.save_conversation(conversation_data=st.session_state.conversations)