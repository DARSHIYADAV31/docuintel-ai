from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import dashboard, documents, health, qa, upload
from app.api.error_handlers import register_error_handlers
from app.auth import routes as auth_routes
from app.config import get_settings
from app.db import models  # noqa: F401  (registers tables on Base)
from app.db.base import Base
from app.db.repositories import document_repo
from app.db.session import get_engine, get_session_factory
from app.logging_setup import get_logger, setup_logging

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(get_settings().log_level)
    Base.metadata.create_all(get_engine())
    with get_session_factory()() as db:
        interrupted = document_repo.fail_interrupted(db)
    log.info("application started interrupted_jobs=%d", interrupted)
    yield


app = FastAPI(title="DocuIntel AI", lifespan=lifespan)
register_error_handlers(app)
for module_router in (auth_routes.router, health.router, upload.router,
                      documents.router, qa.router, dashboard.router):
    app.include_router(module_router)
