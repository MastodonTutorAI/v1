import streamlit as st
from datetime import datetime

service = st.session_state.service

def get_conversation_title(first_message):
    """Generate a title from the first user message"""
    max_title_length = 30
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
                st.session_state.conversations[index]['conversation'] = st.session_state.messages
                st.session_state.conversations[index]['status'] = 'Updated'
            else:
                first_user_message = next(msg["content"] for msg in st.session_state.messages if msg["role"] == "user")
                title = get_conversation_title(first_user_message)
                st.session_state.conversations.append({
                    "title": title,
                    "course_id": service.course_id,
                    "user_id": str(st.session_state.user['_id']),
                    "conversation": st.session_state.messages,
                    "status": 'New'
                })
                st.session_state.selected_conversation = len(st.session_state.conversations) - 1
        except (ValueError, TypeError):
            # If there's any conversion error, treat it as a new conversation
            first_user_message = next(msg["content"] for msg in st.session_state.messages if msg["role"] == "user")
            title = get_conversation_title(first_user_message)
            st.session_state.conversations.append({
                "title": title,
                "course_id": service.course_id,
                "user_id": str(st.session_state.user['_id']),
                "conversation": st.session_state.messages,
                "status": 'New'
            })
            st.session_state.selected_conversation = len(st.session_state.conversations) - 1

def show_conversation():
    # Display past conversations in sidebar
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

    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

def show_assistant():
    # New Chat button
    if st.sidebar.button('New Chat', type='primary'):
        st.session_state.selected_conversation = None
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]
        st.session_state.is_system_prompt = False
    
    # Initialize system prompt if needed
    # if not st.session_state.is_system_prompt:
    #     st.session_state.is_system_prompt = True
    #     st.session_state.messages = [
    #         {"role": "system", "content": service.get_system_prompt()},
    #         {"role": "assistant", "content": "Hello! How can I assist you today?"}
    #     ]

    show_conversation()

    # Handle user input
    if input := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": input})
        with st.chat_message("user"):
            st.write(input)

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Loading..."):
                    # Get response from model
                    # full_response = service.get_response_model(st.session_state.messages)
                    # latest_response = full_response[-1]["content"]
                    st.write(input)  # Placeholder for actual response
            st.session_state.messages.append({"role": "assistant", "content": input})

        save_conversation()
