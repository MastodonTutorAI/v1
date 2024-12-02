import streamlit as st
from page.html_template import template

service = st.session_state.service
fields = ["Course Name", "Professor Name", "Action"]

def get_courses():
    with st.spinner("Fetching courses..."):
        global courses
        user_id = str(st.session_state.user['_id'])
        courses_all_cursor = service.get_all_courses()
        courses_student_cursor = service.get_student_courses(user_id)
        
        student_courses = {course['course_id'] for course in courses_student_cursor}
        courses = []
        
        for course in courses_all_cursor:
            course['enrolled'] = course['course_id'] in student_courses
            courses.append(course)
        
        st.session_state.courses = courses

def enroll_in_course(course_id):
    user_id = str(st.session_state.user['_id'])
    service.create_student_course(user_id, course_id)
    st.toast(f"Enrolled in course {course_id} successfully.")
    st.rerun()

@st.fragment
def show_table():
    container = st.container(border=True)
    with container:
        # Create table header
        cols = st.columns([2, 2, 0.5])
        for col, field in zip(cols, fields):
            html_content = f"<span style='font-weight: bold; font-size: 18px;'>{field}</span>"
            col.markdown(html_content, unsafe_allow_html=True)

        st.divider()

        for course in st.session_state.courses:
            course_name = course['course_name']
            status = course['enrolled']
            col1, col2, col3 = st.columns([2, 2, 0.5])
            col1.write(course_name)
            col2.write(course['professor_name'])
            with col3:
                button_label = 'Already Enrolled' if status else 'Enroll'
                if st.button(button_label, key="enroll" + str(course_name), disabled=status):
                    enroll_in_course(course['course_id'])

def show_courses():
    st.title("Available Courses")
    st.divider() 
    get_courses()
    show_table()

show_courses()