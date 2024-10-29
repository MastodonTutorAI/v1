import streamlit as st

# Sidebar - New Chat button
if "conversations" not in st.session_state:
    st.session_state.conversations = []

# When the New Chat button is clicked, start a new empty conversation
if st.sidebar.button('New Chat', type='primary'):
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state.conversations.append([])

# Display past conversations as clickable buttons in the sidebar
if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = None

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
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.selected_conversation is not None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else:
    # Ensure that the initial messages are displayed when there is no selected conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Simulate a response (you can replace this with your own logic)
    response = f"Echo: {prompt}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Save the conversation
    if st.session_state.selected_conversation is not None:
        st.session_state.conversations[st.session_state.selected_conversation] = st.session_state.messages
    else:
        st.session_state.conversations.append(st.session_state.messages)