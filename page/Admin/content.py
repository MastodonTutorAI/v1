import streamlit as st
from page.html_template import template
import time

# Define columns for the layout
colms = st.columns([2, 1])
fields = ["File Name", "Available To Assistant", "Preview", "Action"]

# File uploader
uploaded_file = colms[0].file_uploader(
    "Choose a file", accept_multiple_files=False, type=['pdf', 'txt', 'pptx'], key=st.session_state['uploader_key']
)

# Render the upload button
st.markdown(
    template.upload_button,
    unsafe_allow_html=True,
)
colms[1].markdown('<span id="upload_button"></span>', unsafe_allow_html=True)
# Define upload button functionality
with st.container():
    if colms[1].button("Upload", key="upload_button", type='primary'):
        if uploaded_file:
            progress_bar = st.progress(0, text='Processing...')
            for percent_complete in range(100):
                time.sleep(0.03) 
                progress_bar.progress(percent_complete + 1)

            st.session_state['uploaded_files'].append({
                "file_name": uploaded_file.name,
                "available": False 
            })
            st.session_state['uploader_key'] += 1
            st.success(f"'{uploaded_file.name}' uploaded successfully!")

# Create a container with a border
container = st.container(border=True)

with container:
    # Create table header
    cols = st.columns([2, 0.5, 0.5, 0.5])
    for col, field in zip(cols, fields):
        html_content = f"""
            <div style='display: flex; align-items: center; justify-content: space-between; width: 100%;'>
                <span style='font-weight: bold; font-size: 18px;'>{field}</span>
            </div>
            """
        col.markdown(html_content, unsafe_allow_html=True)

    st.divider()

    # Show uploaded files in the table if any exist
    if st.session_state['uploaded_files']:
        for file_data in st.session_state['uploaded_files']:
            file_name = file_data['file_name']

            col1, col2, col3, col4 = st.columns([2, 0.5, 0.5, 0.5])

            col1.write(file_name)

            preview_placeholder = col3.empty()
            show_preview = preview_placeholder.button("Preview", key="Preview"+file_name)

            col4.button("Delete", key="Delete"+file_name, on_click=lambda: st.session_state['uploaded_files'].remove(file_data))

            with col2:
                assistant_checkbox = st.checkbox("Available", key="assistant_checkbox_" + file_name, value=file_data['available'])

            file_data['available'] = assistant_checkbox

            if show_preview:
                st.write(f"Previewing file: {file_name}")

    else:
        st.write("No files uploaded yet.")
