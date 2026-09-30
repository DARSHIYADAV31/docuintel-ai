import re

import streamlit as st
from http_client import ApiError
from ui_session import fetch, get_client, require_login

st.title("Ask a question")
require_login()
client = get_client()

READY = ("completed", "needs_review")
documents = [d for d in fetch(client.list_documents) if d["status"] in READY]
if not documents:
    st.info("No processed documents to ask about yet.")
    st.stop()

chosen = st.selectbox("Document", [d["id"] for d in documents],
                      format_func=lambda i: next(f"{d['filename']} (#{d['id']})"
                                                 for d in documents if d["id"] == i))
history = st.session_state.setdefault("qa_history", {}).setdefault(chosen, [])

question = st.text_input("Your question", placeholder="When is payment due?")
if st.button("Ask", type="primary") and question:
    try:
        with st.spinner("Searching the document..."):
            history.append((question, client.ask(chosen, question)))
    except ApiError as exc:
        st.error(str(exc))

for asked, reply in reversed(history):
    st.markdown(f"**Q:** {asked}")
    st.markdown(f"**A:** {re.sub(r'\s*\[\d+\]', '', reply['answer'])}")
    if not reply["grounded"]:
        st.caption("No supporting passage was found in the document.")
    for cite in reply["citations"]:
        st.caption(f"Source (passage {cite['chunk_index'] + 1}): {cite['snippet']}")
    st.divider()
