import streamlit as st
from page.html_template import template
import time
from streamlit_extras.add_vertical_space import add_vertical_space
import io
# import pdfplumber
# from bson.binary import Binary
import fitz

service = st.session_state.service
fields = ["File Name", "Available To Assistant", "Preview", "Action"]
selected_course_id = None

@st.fragment
def retrieve_files():
    # Load files from MongoDB once
    st.session_state['uploaded_files'] = []
    with st.spinner("Loading files..."):
        course_files = service.get_file_db(selected_course_id)
        for file in course_files:
            st.session_state['uploaded_files'].append({
                "file_name": file['file_name'],
                "available": file['available'],
                "file_id": file['file_id']  # Store file_id for referencing
            })

def content_page_header():
    st.title(st.session_state.selected_course['course_name'])
    st.divider()
    st.subheader("Manage Course Material")
    add_vertical_space(1)

@st.fragment
def show_content():
    global selected_course_id
    selected_course_id = st.session_state.selected_course['course_id']
    content_page_header()
    retrieve_files()
    add_vertical_space(1)
    # Define columns for the layout
    colms = st.columns([2, 1])
    
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
    
    # Upload button
    with st.container():
        if colms[1].button("Upload", key="upload_button", type='primary'):
            if uploaded_file:
                with st.spinner('Processing...'):
                    # Pass file_content directly to the service
                    service.create_embedding(uploaded_file, selected_course_id)
                    
                    # Append file details to session state after processing is complete
                    st.session_state['uploader_key'] += 1
                    st.success(f"'{uploaded_file.name}' uploaded successfully!")
                    retrieve_files()
            else:
                st.error("Please upload a valid file.")
    show_table()
    
@st.fragment
def show_table():
    container = st.container(border=True)
    with container:
        # Create table header
        cols = st.columns([2, 0.5, 0.5, 0.5])
        for col, field in zip(cols, fields):
            html_content = f"<span style='font-weight: bold; font-size: 18px;'>{field}</span>"
            col.markdown(html_content, unsafe_allow_html=True)

        st.divider()

        # Display the table of files
        if st.session_state['uploaded_files']:
            for file_data in st.session_state['uploaded_files']:
                file_name = file_data['file_name']
                file_id = file_data['file_id']

                col1, col2, col3, col4 = st.columns([2, 0.5, 0.5, 0.5])

                col1.write(file_name)
                preview_placeholder = col3.empty()
                show_preview = preview_placeholder.button("Preview", key="Preview" + file_name, disabled=True)

                col4.button("Delete", key="Delete" + file_name, on_click=lambda: st.session_state['uploaded_files'].remove(file_data))

                with col2:
                    assistant_checkbox = st.checkbox("Available", key="assistant_checkbox_" + file_name, value=file_data['available'])
                file_data['available'] = assistant_checkbox

                # Show preview if the button is clicked
                # if show_preview:
                #     # Fetch the file binary only when preview is requested
                #     course_material_metadata = service.get_file_by_id(file_id)

                #     if course_material_metadata and 'actual_file' in course_material_metadata:
                #         file_bytes = course_material_metadata['actual_file']

                #         # Process and display PDF content for preview
                #         st.write(f"Previewing file: {file_name}")
                #         with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                #             for page in pdf.pages:
                #                 st.write(page.extract_text())

                #         # Display images in the PDF
                #         pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
                #         for page_num in range(pdf_document.page_count):
                #             page = pdf_document[page_num]
                #             image_list = page.get_images(full=True)
                #             if image_list:
                #                 st.write(f"Images on Page {page_num + 1}:")
                #                 for img_index, img in enumerate(image_list):
                #                     xref = img[0]
                #                     base_image = pdf_document.extract_image(xref)
                #                     image_bytes = base_image["image"]
                #                     st.image(image_bytes, caption=f"Page {page_num + 1} - Image {img_index + 1}")
                #     else:
                #         st.error("File not found in database.")
        else:
            st.write("No files uploaded yet.")