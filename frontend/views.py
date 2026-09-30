"""Small rendering helpers shared by several pages."""
import pandas as pd
import streamlit as st

STATUS_ICON = {"completed": "✅", "needs_review": "⚠️", "failed": "❌", "processing": "⏳"}
SEVERITY_ICON = {"error": "🔴", "warning": "🟡"}


def status_label(status: str) -> str:
    return f"{STATUS_ICON.get(status, '•')} {status}"


def render_fields(fields: list[dict]) -> None:
    frame = pd.DataFrame(fields)
    if frame.empty:
        st.info("No fields were extracted.")
        return
    frame["flagged"] = frame["flagged"].map({True: "⚠️ review", False: ""})
    st.dataframe(frame, hide_index=True, use_container_width=True)


def render_line_items(items: list[dict]) -> None:
    if items:
        st.dataframe(pd.DataFrame(items), hide_index=True, use_container_width=True)


def render_issues(issues: list[dict]) -> None:
    for issue in issues:
        icon = SEVERITY_ICON.get(issue["severity"], "•")
        st.write(f"{icon} **{issue['field_name']}** ({issue['rule']}): {issue['message']}")


def render_cost(summary: dict | None) -> None:
    llm = (summary or {}).get("llm")
    if not llm:
        return
    calls, tokens, cost = st.columns(3)
    calls.metric("LLM calls", llm["calls"])
    tokens.metric("Tokens", llm["input_tokens"] + llm["output_tokens"])
    cost.metric("Estimated cost", f"${llm['estimated_usd']:.4f}")
