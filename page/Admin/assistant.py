import streamlit as st

service = st.session_state.service

# Function to delete a conversation
def delete_conversation(index):
    del st.session_state.conversations[index]
    # If the deleted conversation was selected, reset the selected conversation
    if st.session_state.selected_conversation == index:
        st.session_state.selected_conversation = None
        st.session_state.messages = []
    # If a conversation after the deleted one was selected, shift the selection
    elif st.session_state.selected_conversation is not None and st.session_state.selected_conversation > index:
        st.session_state.selected_conversation -= 1

def save_conversation():
    # Save the conversation
    if st.session_state.selected_conversation is not None:
        st.session_state.conversations[st.session_state.selected_conversation] = st.session_state.messages
    else:
        st.session_state.conversations.append(st.session_state.messages)

def show_conversation():
    if st.session_state.selected_conversation is not None:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    else:
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

def show_assistant():
    # When the New Chat button is clicked, start a new empty conversation
    if st.sidebar.button('New Chat', type='primary'):
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
        st.session_state.conversations.append([])
    
    # Display past conversations as clickable buttons in the sidebar
    if "selected_conversation" not in st.session_state:
        st.session_state.selected_conversation = None

    for i, conversation in enumerate(st.session_state.conversations):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if col1.button(f"Conversation {i + 1}"):
                st.session_state.selected_conversation = i
                st.session_state.messages = conversation
        with col2:
            if col2.button(label="",icon=":material/delete:", key=f"delete_{i}",):
                delete_conversation(i)
    
    st.caption("🚀 AI assistant of Prof. Zesheng Chen")

    # Display chat messages from selected conversation
    if st.session_state.is_system_prompt == False:
        st.session_state.is_system_prompt = True
        st.session_state.messages = [{"role": "system", "content": service.get_system_prompt()}, {"role": "assistant", "content": "How can I help you?"}]

    show_conversation()
    
    if input := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": input})
        with st.chat_message("user"):
            st.write(input)

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Loading..."):
                    print(st.session_state.messages)
                    print("--------------------")
                    # full_response = service.get_response_model(st.session_state.messages)
                    # latest_response = full_response[-1]["content"]
                    latest_response = input
                    st.write(latest_response)
            st.session_state.messages.append({"role": "assistant", "content": latest_response})

        save_conversation()