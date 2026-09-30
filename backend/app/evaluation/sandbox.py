import tempfile
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.repositories import user_repo
from app.vectorstore.faiss_store import FaissStore


@contextmanager
def eval_sandbox():
    """Throwaway SQLite DB and vector store, so evaluation never touches real data."""
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with tempfile.TemporaryDirectory() as tmp:
        db = factory()
        owner = user_repo.create_user(db, "evaluator", "not-a-real-hash")
        db.close()
        yield factory, FaissStore(Path(tmp)), owner.id
