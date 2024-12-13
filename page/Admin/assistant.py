import streamlit as st
from datetime import datetime
import time

service = st.session_state.service

def show_stream(data):
    for word in data.split(" "):
        yield word + " "
        time.sleep(0.02)

def get_conversation_title(first_message):
    max_title_length = 25
    title = first_message[:max_title_length]
    if len(first_message) > max_title_length:
        title += "..."
    return title

def delete_conversation(index):
    try:
        index = int(index)
        if 0 <= index < len(st.session_state.conversations):
            service.remove_conversation(st.session_state.conversations[index]['_id'])
            del st.session_state.conversations[index]
            if st.session_state.selected_conversation == index:
                st.session_state.selected_conversation = None
                st.session_state.messages = []
            elif st.session_state.selected_conversation is not None:
                current_index = int(st.session_state.selected_conversation)
                st.session_state.selected_conversation = max(0, current_index - 1)
    except (ValueError, TypeError):
        st.session_state.selected_conversation = None

def save_conversation():
    if any(msg["role"] == "user" for msg in st.session_state.messages):
        try:
            if (st.session_state.selected_conversation is not None and 
                str(st.session_state.selected_conversation).strip()):
                index = int(st.session_state.selected_conversation)
                if st.session_state.conversations[index]['status'] != 'New':
                    st.session_state.conversations[index]['status'] = 'Updated'
                st.session_state.conversations[index]['conversation'] = st.session_state.messages
            else:
                first_user_message = next(msg["content"] for msg in st.session_state.messages if msg["role"] == "user")
                title = get_conversation_title(first_user_message)
                new_conversation = {
                    "title": title,
                    "course_id": service.course_id,
                    "user_id": str(st.session_state.user['_id']),
                    "conversation": st.session_state.messages,
                    "status": 'New'
                }
                st.session_state.conversations.append(new_conversation)
                st.session_state.selected_conversation = len(st.session_state.conversations) - 1
        except (ValueError, TypeError) as e:
            first_user_message = next(msg["content"] for msg in st.session_state.messages if msg["role"] == "user")
            title = get_conversation_title(first_user_message)
            new_conversation = {
                "title": title,
                "course_id": service.course_id,
                "user_id": str(st.session_state.user['_id']),
                "conversation": st.session_state.messages,
                "status": 'New'
            }
            st.session_state.conversations.append(new_conversation)
            st.session_state.selected_conversation = len(st.session_state.conversations) - 1

def show_conversation():
    if st.session_state.conversations:
        st.sidebar.markdown("### Previous Chats")
        for i, conversation in enumerate(st.session_state.conversations):
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                try:
                    is_selected = (st.session_state.selected_conversation is not None and 
                                 int(st.session_state.selected_conversation) == i)
                except (ValueError, TypeError):
                    is_selected = False
                
                button_style = "primary" if is_selected else "secondary"
                if col1.button(conversation["title"], key=f"conv_{i}", type=button_style):
                    st.session_state.selected_conversation = i
                    st.session_state.messages = conversation["conversation"]
                    st.rerun()
            with col2:
                if col2.button("🗑️", key=f"delete_{i}"):
                    delete_conversation(i)
                    st.rerun()

    if st.session_state.messages == []:
        response = st.session_state.conversation_manager.get_response(
                user_input="Greet me in short.",
                context="skip",
                selected_conversation=None
            )
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

def show_assistant():
    service = st.session_state.service

    if st.sidebar.button('New Chat', type='primary'):
        st.session_state.selected_conversation = None
        st.session_state.messages = []
        st.session_state.conversation_manager.clear_history()
        
        with st.spinner("Loading..."):
            response = st.session_state.conversation_manager.get_response(
                user_input="Greet me in short.",
                context="skip",
                selected_conversation=None
            )
            st.session_state.messages.append({"role": "assistant", "content": response})

    show_conversation()
    
    if input := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": input})
        with st.chat_message("user"):
            st.write(input)

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Loading..."):
                    selected_conv = None
                    if st.session_state.selected_conversation is not None:
                        selected_conv = st.session_state.conversations[st.session_state.selected_conversation]
                    
                    response = st.session_state.conversation_manager.get_response(
                        user_input=input,
                        context=service.search_vector(input, 5),
                        selected_conversation=selected_conv
                    )
                    st.write(show_stream(response))
            st.session_state.messages.append({"role": "assistant", "content": response})

        save_conversation()
