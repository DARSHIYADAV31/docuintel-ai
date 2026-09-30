import streamlit as st
from polling import wait_for_result
from ui_session import fetch, get_client, require_login
from views import render_issues, status_label

st.title("Upload a document")
require_login()

MIME = {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg",
        "jpeg": "image/jpeg", "tif": "image/tiff", "tiff": "image/tiff"}

upload = st.file_uploader("PDF, scan, or photo (max 20 MB)", type=list(MIME))
handwritten = st.checkbox("This document is handwritten (uses the handwriting OCR)")

if upload and st.button("Process document", type="primary"):
    client = get_client()
    ext = upload.name.rsplit(".", 1)[-1].lower()
    accepted = fetch(client.upload, upload.name, upload.getvalue(), MIME[ext], handwritten)
    with st.spinner("Reading and analysing the document..."):
        result = fetch(wait_for_result, client, accepted["id"])
    if result is None:
        st.warning("Still processing. Check the Documents page in a minute.")
        st.stop()
    kind = f" - {result['doc_type']}" if result["doc_type"] else ""
    st.subheader(f"{status_label(result['status'])}{kind}")
    if result["error_message"]:
        st.error(result["error_message"])
    if result["confidence"] is not None:
        st.progress(result["confidence"], text=f"Confidence {result['confidence']:.0%}")
    render_issues(result["issues"])
    st.caption("Open the Documents page for the extracted fields.")
