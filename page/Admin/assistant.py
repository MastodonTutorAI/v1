import streamlit as st

service = st.session_state.service

# Function to delete a conversation
def delete_conversation(index):
    del st.session_state.conversations[index]
    if st.session_state.selected_conversation == index:
        st.session_state.selected_conversation = None
        st.session_state.messages = []
    elif st.session_state.selected_conversation is not None and st.session_state.selected_conversation > index:
        st.session_state.selected_conversation -= 1

# Function to save the current conversation
def save_conversation():
    if st.session_state.selected_conversation is not None:
        st.session_state.conversations[st.session_state.selected_conversation] = st.session_state.messages.copy()
    else:
        st.session_state.conversations.append(st.session_state.messages.copy())

# Function to display the chat messages
def show_conversation():
    for message in st.session_state.messages:
        if message["role"] != "system":  # Skip system messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Main assistant interface
def show_assistant():
    st.sidebar.header("Conversations")

    # Button to start a new chat
    if st.sidebar.button("New Chat", type="primary"):
        st.session_state.messages = []
        st.session_state.selected_conversation = None
        st.session_state.is_system_prompt = False

    # Display past conversations as clickable buttons in the sidebar
    for i, conversation in enumerate(st.session_state.conversations):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if col1.button(f"Conversation {i + 1}"):
                st.session_state.selected_conversation = i
                st.session_state.messages = conversation
        with col2:
            if col2.button("🗑", key=f"delete_{i}"):
                delete_conversation(i)
                st.rerun()  # Refresh UI immediately

    # Set up a new conversation if no existing conversation is selected
    if st.session_state.selected_conversation is None:
        if not st.session_state.is_system_prompt:
            st.session_state.messages = [
                {"role": "system", "content": service.get_system_prompt() if service else "Default system prompt"},
                {"role": "assistant", "content": "How can I help you?"}
            ]
            st.session_state.is_system_prompt = True
        else:
            # Ensure default new chat messages exist
            st.session_state.messages = [
                {"role": "system", "content": service.get_system_prompt() if service else "Default system prompt"},
                {"role": "assistant", "content": "How can I help you?"}
            ]

    # Display chat messages
    show_conversation()

    # Input box for user messages
    if input_message := st.chat_input("What is up?"):
        if st.session_state.selected_conversation is None:
            # Start a new conversation if it's not tied to an existing one
            st.session_state.selected_conversation = len(st.session_state.conversations)
            st.session_state.conversations.append([])

        # Add user input to messages
        st.session_state.messages.append({"role": "user", "content": input_message})
        with st.chat_message("user"):
            st.write(input_message)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Loading..."):
                latest_response = input_message  # Replace with your service call
                st.write(latest_response)

        st.session_state.messages.append({"role": "assistant", "content": latest_response})
        save_conversation()