import streamlit as st
from page.Admin.content import show_content
from page.Admin.assistant import show_assistant

admin_assistant = st.Page("page/Admin/assistant.py", title="Assistant", icon=":material/chat:")

service = st.session_state.service
courses = st.session_state.courses

def get_conversation():
    if st.session_state['conversation_fetch_flag'] == True:
        #Get Conversations
        with st.spinner("Loading..."):
            st.session_state.conversations = list(service.get_conversation(str(st.session_state.user['_id'])))
        for conversation in st.session_state.conversations:
            conversation['status'] = 'Updated'
        st.session_state['conversation_fetch_flag'] = False

@st.dialog("Create New Course")
def create_new_assistant():
    st.caption("All are required fields")
    course_name = st.text_input("Course Name", "", placeholder="e.g. Deep Learning")
    course_id = st.text_input("Course Id", placeholder="e.g. CS5900")
    professor_name = st.text_input("Professor Name", "")
    description = st.text_area("Description","")
    if st.button("Submit"):
        if course_name == "" or course_id == "" or professor_name == "" or description == "":
            st.error("Please fill all the fields!")
            return
        with st.spinner("Creating new course..."):
            try:
                course_id = service.create_course(course_id, course_name, professor_name, description, st.session_state.user['_id'])
                st.success("Course created successfully!")
                get_courses()
                st.rerun()
            except Exception as e:
                st.error(e)

def get_courses():
    with st.spinner("Fetching courses..."):
        global courses
        courses_cursor = service.get_courses(st.session_state.user['_id'])
        courses = {}
        for course in courses_cursor:
            courses[course['course_id']] = course 
        st.session_state.courses = dict(courses)

@st.fragment
def course_row(course):
    with st.container(border=True):
        with st.container(border = False , height=300):
            st.subheader(course['course_name'])
            st.write(f"**Professor:** {course['professor_name']}")
            st.write(f"**Course Id:** {course['course_id']}")
            st.write(f"**Description:** {course['description']}")
            cols = st.columns([1, 6])
            cols[0].success("**Status:** Active", icon="✅")

        st.divider()
        cols = st.columns([1, 1, 1, 6])

        # Button to view content details
        if cols[0].button("View Details", key=f"content_details_{course['course_id']}"):
            print("View content details")
            st.session_state['content_opened'] = True
            st.session_state['selected_course'] = course
            service.set_course_details(course)
            st.rerun()

        # Button to view assistant
        if cols[1].button("View Assistant", key=f"assistant_details_{course['course_id']}"):
            st.session_state['assistant_opened'] = True
            st.session_state['conversation_fetch_flag'] = True
            st.session_state['selected_course'] = course
            service.set_course_details(course)
            st.rerun()
        
        if cols[2].button("Delete Course", key=f"delete_course_{course['course_id']}", type="primary"):
            service.set_course_details(course)
            if service.remove_course():
                st.toast('Course deleted successfully')
                get_courses()
                st.rerun()

def show_courses():
    with st.container(border=False):
        for course_id, course in st.session_state.courses.items():  # Iterate over key-value pairs
            course_row(course)

def dashboard_main():
    st.title("Available Courses")
    st.divider() 
    if st.button("Create New Course", key="create_course"):
        create_new_assistant()

    show_courses()

def reset_session_state():
    st.session_state['content_opened'] = False
    st.session_state['assistant_opened'] = False
    st.session_state['selected_course'] = None
    st.session_state['uploaded_files'] = []
    st.session_state['messages'] = []
    st.session_state['is_system_prompt'] = False
    st.session_state['selected_conversation'] = None

def dashboard():
    get_courses()

    if st.session_state['content_opened'] == False and st.session_state['assistant_opened'] == False:
        dashboard_main()
    else:
        if st.button("Go back"):
            if st.session_state['assistant_opened'] == True:
                #Save Conversations
                service.save_conversation(conversation_data=st.session_state.conversations)
            
            reset_session_state()
            st.rerun()

        if st.session_state['content_opened'] == True:
            show_content()

        if st.session_state['assistant_opened'] == True:
            st.divider()
            st.subheader("**Assistant For "+ st.session_state['selected_course']['course_name'] + "**")
            st.caption("🚀 AI assistant of " + st.session_state['selected_course']['professor_name'])
            
            st.session_state.conversation_manager = service.get_model_conversation()
            get_conversation()
            show_assistant()

dashboard()
