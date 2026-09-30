import pandas as pd
import streamlit as st
from ui_session import fetch, get_client, require_login

st.title("Confidence and accuracy")
require_login()
client = get_client()

st.subheader("Extraction accuracy (labeled test set)")
evaluation = fetch(client.dashboard)["latest_evaluation"]
if evaluation is None:
    st.info("No evaluation run yet. Run `python run_eval.py --save-to-db`.")
else:
    overall, doc_type = st.columns(2)
    overall.metric("Overall field accuracy", f"{evaluation['overall_accuracy']:.1%}")
    kind = evaluation["doc_type_accuracy"]
    doc_type.metric("Document type accuracy", f"{kind:.0%}" if kind is not None else "n/a")
    st.caption(f"Last run: {evaluation['created_at']}")
    per_field = pd.Series(evaluation["per_field_accuracy"], name="accuracy").dropna()
    st.bar_chart(per_field)

st.subheader("Confidence per processed document")
scored = [d for d in fetch(client.list_documents) if d["confidence"] is not None]
if scored:
    frame = pd.DataFrame(scored).set_index("filename")["confidence"]
    st.bar_chart(frame)
else:
    st.info("No scored documents yet.")
