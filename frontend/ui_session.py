import os
from pathlib import Path

import streamlit as st
from api_client import ApiClient
from dotenv import load_dotenv
from http_client import ApiError

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_client() -> ApiClient:
    tokens = st.session_state.setdefault("tokens", {})
    return ApiClient(os.getenv("API_BASE_URL", "http://localhost:8000"), tokens)


def is_logged_in() -> bool:
    return bool(st.session_state.get("tokens", {}).get("access"))


def sidebar() -> None:
    if is_logged_in() and st.sidebar.button("Log out"):
        st.session_state["tokens"] = {}
        st.rerun()


def require_login() -> None:
    sidebar()
    if not is_logged_in():
        st.warning("Please log in on the Home page first.")
        st.stop()


def fetch(call, *args, **kwargs):
    """Runs an API call; shows the error and stops the page if it fails."""
    try:
        return call(*args, **kwargs)
    except ApiError as exc:
        st.error(str(exc))
        st.stop()
