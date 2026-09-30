import pandas as pd
import streamlit as st
from ui_session import fetch, get_client, require_login
from views import render_cost, render_fields, render_line_items, status_label

st.title("Documents")
require_login()
client = get_client()

documents = fetch(client.list_documents)
if not documents:
    st.info("No documents yet. Upload one first.")
    st.stop()

table = pd.DataFrame(documents)
table["status"] = table["status"].map(status_label)
st.dataframe(table[["id", "filename", "doc_type", "status", "confidence", "created_at"]],
             hide_index=True, width="stretch")

chosen = st.selectbox("Open a document", [d["id"] for d in documents],
                      format_func=lambda i: next(d["filename"] for d in documents if d["id"] == i))
reveal = st.checkbox("Show sensitive fields in full (this access is logged)")
detail = fetch(client.get_document, chosen, reveal)

st.subheader(f"{detail['filename']} - {status_label(detail['status'])}")
if detail["error_message"]:
    st.error(detail["error_message"])
render_cost(detail["processing_summary"])
st.write("**Extracted fields**")
render_fields(detail["fields"])
if detail["line_items"]:
    st.write("**Line items**")
    render_line_items(detail["line_items"])
