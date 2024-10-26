import streamlit as st
from utils import init as init_page

st.set_page_config(
    page_title="Mastodon TutorAI",
    page_icon=":material/school:",
    layout="wide"
)

admin_dashboard = st.Page("page/Admin/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
admin_reports = st.Page("page/Admin/reports.py", title="Report", icon=":material/lab_profile:")
admin_contents = st.Page("page/Admin/content.py", title="Content", icon=":material/file_copy:")
logout = st.Page("page/logout.py", title="Log out", icon=":material/logout:")
login = st.Page("page/login.py", title="LogIn", icon=":material/login:")
admin_assistant = st.Page("page/Admin/assistant.py", title="Assistant Settings", icon=":material/chat:")
student_assistant = st.Page("page/Student/assistant.py", title="Assistant", icon=":material/chat:")
quiz = st.Page("page/Student/quiz.py", title="Quiz", icon=":material/quiz:")

def main():
    init_page.init_page()
    if st.session_state.isLogined:
        # Admin Pages
        if st.session_state.isAdmin == True:
            pg_admin = st.navigation(
                {
                    "Account": [admin_dashboard, admin_reports],
                    "Assistant": [admin_assistant, quiz],
                    "Settings": [logout]
                },
                position='sidebar'
            )
            pg_admin.run()
        else:
            # Student Pages
            pg_student = st.navigation(
                {
                    "Assistant": [student_assistant, quiz],
                    "Settings": [logout]
                },
                position='sidebar'
            )
            pg_student.run()
    else:
        pg = st.navigation(
            [login],
            position='sidebar',
            expanded=False
        )
        pg.run()

if __name__ == "__main__":
    main()
