import streamlit as st
from http_client import ApiError
from ui_session import get_client

st.title("DocuIntel AI")
st.caption("Invoice and contract review for AP and Legal teams")


def auth_form(label: str, action) -> None:
    with st.form(label):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button(label):
            try:
                action(username, password)
            except ApiError as exc:
                st.error(str(exc))
            else:
                st.rerun()


client = get_client()
login_tab, register_tab = st.tabs(["Log in", "Create account"])
with login_tab:
    auth_form("Log in", client.login)
with register_tab:
    auth_form("Create account", client.register)
