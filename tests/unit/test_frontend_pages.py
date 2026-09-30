"""Smoke-runs each Streamlit page to catch import/syntax/runtime errors."""
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
sys.path.insert(0, str(FRONTEND))

PAGES = ["Home.py", "pages/1_Upload.py", "pages/2_Documents.py", "pages/3_Ask.py",
         "pages/4_Issues.py", "pages/5_Accuracy.py"]


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_without_error_when_logged_out(page):
    app = AppTest.from_file(str(FRONTEND / page), default_timeout=20).run()
    assert not app.exception


def test_protected_pages_ask_for_login():
    app = AppTest.from_file(str(FRONTEND / "pages/2_Documents.py"), default_timeout=20).run()
    assert any("log in" in w.value.lower() for w in app.warning)


def test_home_shows_login_and_signup_tabs():
    app = AppTest.from_file(str(FRONTEND / "Home.py"), default_timeout=20).run()
    assert len(app.tabs) == 2
