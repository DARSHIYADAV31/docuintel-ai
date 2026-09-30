from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


@lru_cache
def get_engine():
    # pre_ping drops dead connections instead of failing the request
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session_factory():
    """Background tasks outlive the request, so they open their own session."""
    return sessionmaker(bind=get_engine())


def get_db():
    session: Session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
