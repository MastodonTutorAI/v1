import streamlit as st
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

def get_courses():
    with st.spinner("Fetching courses..."):
        global courses
        user_id = str(st.session_state.user['_id'])
        courses_cursor = service.get_student_courses(user_id)
        courses = {}
        for course in courses_cursor:
            courses[course['course_id']] = course 
        st.session_state.courses = courses

@st.fragment
def course_row(course):
    with st.container(border=True, height=400):
        st.subheader(course['course_name'])
        st.write(f"**Professor:** {course['professor_name']}")
        st.write(f"**Course Id:** {course['course_id']}")
        st.write(f"**Description:** {course['description']}")
        cols = st.columns([1, 6])
        cols[0].success("**Status:** Active", icon="✅")

        st.divider()
        cols = st.columns(1)

        # Button to view assistant
        if cols[0].button("View Assistant", key=f"assistant_details_{course['course_id']}"):
            st.session_state['assistant_opened'] = True
            st.session_state['conversation_fetch_flag'] = True
            st.session_state['selected_course'] = course
            service.set_course_id(course['course_id'])
            st.rerun()
        
def show_courses():
    with st.container(border=False):
        for course_id, course in st.session_state.courses.items():  # Iterate over key-value pairs
            course_row(course)

def dashboard_main():
    st.title("Available Courses")
    st.divider() 
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
    if st.session_state.courses == []:
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

        if st.session_state['assistant_opened'] == True:
            st.divider()
            st.subheader("**Assistant For "+ st.session_state['selected_course']['course_name'] + "**")
            st.caption("🚀 AI assistant of " + st.session_state['selected_course']['professor_name'])
            course_name = st.session_state['selected_course']['course_name']
            st.session_state.conversation_manager = service.get_model_conversation(course_name)
            get_conversation()
            show_assistant()

dashboard()
