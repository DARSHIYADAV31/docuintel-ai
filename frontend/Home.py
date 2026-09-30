import streamlit as st
from ui_session import is_logged_in

st.set_page_config(page_title="DocuIntel AI", page_icon="📄", layout="wide")

if is_logged_in():
    pages = [
        st.Page("overview_page.py", title="Dashboard", icon="📊", default=True),
        st.Page("pages/1_Upload.py", title="Upload", icon="📤"),
        st.Page("pages/2_Documents.py", title="Documents", icon="📄"),
        st.Page("pages/3_Ask.py", title="Ask", icon="💬"),
        st.Page("pages/4_Issues.py", title="Issues", icon="⚠️"),
        st.Page("pages/5_Accuracy.py", title="Accuracy", icon="🎯"),
    ]
    navigation = st.navigation(pages)
else:
    # nothing but the login form is reachable until the user signs in
    navigation = st.navigation([st.Page("login_page.py", title="Log in")], position="hidden")

navigation.run()
