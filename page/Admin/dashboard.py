import streamlit as st
from page.Admin.content import show_content
from page.Admin.assistant import show_assistant

admin_assistant = st.Page("page/Admin/assistant.py", title="Assistant", icon=":material/chat:")

service = st.session_state.service
courses = st.session_state.courses
# st.write(st.session_state.user)

@st.dialog("Create New Assistant")
def create_new_assistant():
    course_name = st.text_input("Course Name", "")
    professor_name = st.text_input("Professor Name", "")
    description = st.text_area("Description","")
    if st.button("Submit"):
        with st.spinner("Creating new assistant..."):
            course_id = service.create_course(course_name, professor_name, description, st.session_state.user['_id'])
            st.success("Assistant created successfully!")
            get_courses()

def get_courses():
    with st.spinner("Fetching courses..."):
        global courses
        courses_cursor = service.get_courses(st.session_state.user['_id'])
        courses = {}
        for course in courses_cursor:
            courses[course['course_id']] = course  # Use course_id as key
        st.session_state.courses = courses

@st.fragment
def course_row(course):
    with st.container(border=True, height=400):
        st.subheader(course['course_name'])
        st.write(f"**Professor:** {course['professor_name']}")
        st.write(f"**Description:** {course['description']}")
        cols = st.columns([1, 6])
        cols[0].success("**Status:** Active", icon="✅")

        st.divider()
        cols = st.columns([1, 1, 11])

        # Button to view content details
        if cols[0].button("View Details", key=f"content_details_{course['course_id']}"):
            print("View content details")
            st.session_state['content_opened'] = True
            st.session_state['selected_course'] = course
            st.rerun()

        # Button to view assistant
        if cols[1].button("View Assistant", key=f"assistant_details_{course['course_id']}"):
            st.session_state['assistant_opened'] = True
            st.session_state['selected_course'] = course
            st.rerun()

def show_courses():
    with st.container(border=False, height=1000):
        for course_id, course in st.session_state.courses.items():  # Iterate over key-value pairs
            course_row(course)

def dashboard_main():
    st.title("Available Courses")
    st.divider() 
    if st.button("Create New Course", key="create_course"):
        create_new_assistant()

    show_courses()

def dashboard():
    if st.session_state.courses == []:
        get_courses()

    # print("Courses: " + str(st.session_state.courses))
    # print("Courses: " + str(courses))
    if st.session_state['content_opened'] == False and st.session_state['assistant_opened'] == False:
        dashboard_main()
    else:
        if st.button("Go back"):
            if st.session_state['content_opened'] == True or st.session_state['assistant_opened'] == True:
                st.session_state['content_opened'] = False
                st.session_state['assistant_opened'] = False
                st.session_state['selected_course'] = None
                st.session_state['uploaded_files'] = []
                st.rerun()

        if st.session_state['content_opened'] == True:
            show_content()

        if st.session_state['assistant_opened'] == True:
            st.divider()
            st.subheader("**Assistant For Deep Learning Course**")
            show_assistant()

dashboard()