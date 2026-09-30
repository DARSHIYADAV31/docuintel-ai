import streamlit as st
from ui_session import fetch, get_client, require_login
from views import render_issues, status_label

st.title("Flagged issues")
require_login()
client = get_client()

flagged = fetch(client.dashboard)["flagged_documents"]
if not flagged:
    st.success("Nothing needs review.")
    st.stop()

st.caption(f"{len(flagged)} document(s) need attention")
for summary in flagged:
    detail = fetch(client.get_document, summary["id"])
    with st.expander(f"{status_label(detail['status'])}  {detail['filename']}"):
        if detail["error_message"]:
            st.error(detail["error_message"])
        render_issues(detail["issues"])
