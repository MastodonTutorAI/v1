import streamlit as st
from page.html_template import template
import time
from streamlit_extras.add_vertical_space import add_vertical_space
import io


service = st.session_state.service
fields = ["File Name", "Available To Assistant", "Preview", 'RAG Status', "Action"]
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
                "file_id": file['_id'],
                "status": file['status'],
                "summary": file['summary']
            })


def content_page_header():
    st.title(st.session_state.selected_course['course_name'])
    st.divider()
    st.subheader("Manage Course Material")
    add_vertical_space(1)

class StreamlitFileWrapper:
    def __init__(self, uploaded_file):
        self._file = uploaded_file
        self.name = uploaded_file.name
        self.type = uploaded_file.type
        self.value = uploaded_file.read()  
        self._file.seek(0)  

    def read(self, size=-1):
        """Read the file content."""
        if size == -1:
            return self.value
        return self.value[:size]

    def getvalue(self):
        """Return the file content as bytes."""
        return self.value
    
@st.fragment
def show_content():
    global selected_course_id
    selected_course_id = st.session_state.selected_course['course_id']
    content_page_header()
    retrieve_files()
    add_vertical_space(1)
    service.set_course_details(st.session_state['selected_course'])
    # Define columns for the layout
    colms = st.columns([2, 1])

    # File uploader
    uploaded_files = colms[0].file_uploader(
        "Choose files", accept_multiple_files=True, type=['pdf', 'txt', 'pptx'], key=st.session_state['uploader_key']
    )

    # Render the upload button
    st.markdown(
        template.upload_button,
        unsafe_allow_html=True,
    )
    colms[1].markdown('<span id="upload_button"></span>',
                      unsafe_allow_html=True)

    # Upload button
    with st.container():
        if colms[1].button("Upload", key="upload_button", type='primary'):
            if uploaded_files:
                with st.spinner('Processing...'):
                    for uploaded_file in uploaded_files:
                        wrapped_file = StreamlitFileWrapper(uploaded_file)

                        # Process each file individually
                        service.save_file(wrapped_file)

                    # Append file details to session state after processing is complete
                    st.session_state['uploader_key'] += 1
                    st.success("All files uploaded successfully!")
                    retrieve_files()
            else:
                st.error("Please upload valid files.")
    show_table()

def set_course_after_update():
    courses_cursor = service.get_courses(st.session_state.user['_id'])
    courses = {}
    for course in courses_cursor:
        course_id = course['course_id']
        if st.session_state['selected_course']['course_id'] == course_id:
            print('Fetched Updated Course')
            st.session_state['selected_course'] = course
    service.set_course_details(st.session_state['selected_course'])

@st.fragment
def show_table():
    container = st.container(border=True)
    with container:
        # Create table header
        cols = st.columns([1.5, 0.5, 0.5, 0.5, 0.5])
        for col, field in zip(cols, fields):
            html_content = f"<span style='font-weight: bold; font-size: 18px;'>{field}</span>"
            col.markdown(html_content, unsafe_allow_html=True)

        st.divider()

        # Display the table of files
        if st.session_state['uploaded_files']:
            for file_data in st.session_state['uploaded_files']:
                file_name = file_data['file_name']
                file_id = file_data['file_id']
                file_status = file_data['status']
                document_summary = file_data['summary']
                status_flag = True if file_status == 'Processing' or file_status == 'Failed' else False
                delete_flag = True if file_status == 'Processing' else False

                col1, col2, col3, col4, col5 = st.columns([1.5, 0.5, 0.5, 0.5, 0.5])

                col1.write(file_name)
                col4.write(file_status)
                preview_placeholder = col3.empty()
                show_preview = preview_placeholder.button(
                    "Preview", key="Preview" + str(file_id), disabled=True)

                with col5:
                    if st.button("Delete", key="Delete" + str(file_id), disabled=delete_flag):
                        file_id = file_data['file_id']
                        if service.delete_file(file_id):
                            st.session_state['uploaded_files'].remove(
                                file_data)
                            st.toast(
                                'Availability updated for file: ' + file_name)
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.toast('Something went wrong.')

                with col2:
                    if file_data['available']:
                        button_label = "Revoke Access"
                    else:
                        button_label = "Grant Access"

                    if st.button(button_label, key="availability_button_" + str(file_id), disabled=status_flag):
                        value = file_data['available'] = not file_data['available']
                        file_id = file_data['file_id']
                        file_name = file_data['file_name']
                        if service.set_assistant_available(file_id, document_summary, value):
                            st.toast(
                                'Availability updated for file: ' + file_name)
                            set_course_after_update()
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.toast('Something went wrong.')

                        # st.write(f"File ID: {file_id}")
        else:
            st.write("No files uploaded yet.")