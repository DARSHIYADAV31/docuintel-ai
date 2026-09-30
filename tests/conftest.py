import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db, get_session_factory
from app.main import app


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_session_factory] = lambda: (lambda: db_session)
    yield TestClient(app)
    app.dependency_overrides.clear()
