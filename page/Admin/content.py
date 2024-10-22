import streamlit as st
import base64
from io import BytesIO
import os
from streamlit_pdf_viewer import pdf_viewer


# # Function to create a link to download/open the PDF
# def create_pdf_preview_link(file_path):
#     # Create an anchor tag for opening the file in a new tab
#     href = f'<a href="file://{file_path}" target="_blank">Preview PDF in new tab</a>'
#     return href

# @st.fragment
# def show_pdf_preview():
#     if uploaded_file.type == "application/pdf":
#         pdf_viewer(r'assets\Network_Basics.pdf')
#     else:
#         st.write("Preview is not supported for this file type.")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a file", accept_multiple_files=False, type=['pdf', 'txt', 'pptx']
)

fields = ["File Name", "Available To Assistant", "Preview"]

st.markdown("""
    <style>
    .stContainer {
        border: 1px solid black;
        padding: 10px;
        border-radius: 5px;
    }
    .stColumns > div {
        display: flex;
        align-items: center;
        justify-content: center;
        border-right: 1px solid black;
    }
    .stColumns > div:last-child {
        border-right: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Create a container with a border
container = st.container(border=True)

with container:
    # Create table header
    cols = st.columns([2,1,1])
    for col, field in zip(cols, fields):
        col.write(f"**{field}**")

    st.divider()  # Divider line between header and rows

    # Check if a file is uploaded
    if uploaded_file:
        file_name = uploaded_file.name

        # Create table rows for each file
        col1, col2, col3 = st.columns([2,1,1])

        # First column: File Name
        col1.write(file_name)

        # Second column: Preview Button
        preview_placeholder = col3.empty()
        show_preview = preview_placeholder.button("Preview", key=file_name, type='primary')

        # Third column: Checkbox
        with col2:
            assistant_checkbox = st.toggle("Available", key="assistant_checkbox_" + file_name)

        # If checkbox is selected
        if assistant_checkbox:
            st.write(f"The file '{file_name}' is available for the assistant.")

        # If preview button is clicked
        if show_preview:
            st.write(f"Previewing file: {file_name}")

    else:
        st.write('No file uploaded!')
