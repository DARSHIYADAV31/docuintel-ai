import streamlit as st
from ui_session import fetch, get_client, require_login
from views import status_label

st.title("Dashboard")
require_login()

data = fetch(get_client().dashboard)
docs, confidence, cost = st.columns(3)
docs.metric("Documents", data["total_documents"])
average = data["average_confidence"]
confidence.metric("Average confidence", f"{average:.0%}" if average is not None else "n/a")
cost.metric("LLM cost", f"${data['total_cost_usd']:.4f}")

st.subheader("By status")
for status, count in data["by_status"].items():
    st.write(f"{status_label(status)}: **{count}**")

issues = data["issue_counts"]
st.subheader("Open issues")
st.write(f"🔴 errors: **{issues.get('error', 0)}**  🟡 warnings: **{issues.get('warning', 0)}**")
