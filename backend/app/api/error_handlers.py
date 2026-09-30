from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.errors import (DocuIntelError, FileValidationError, ModelUnavailableError,
                        OCRError, VectorStoreError)
from app.logging_setup import get_logger

log = get_logger(__name__)
STATUS_BY_ERROR = {
    FileValidationError: 422,
    ModelUnavailableError: 502,
    OCRError: 502,
    VectorStoreError: 503,
}


def _reply(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DocuIntelError)
    async def app_error(request: Request, exc: DocuIntelError):
        log.error("request failed error=%s", type(exc).__name__)
        return _reply(STATUS_BY_ERROR.get(type(exc), 400), str(exc))

    @app.exception_handler(SQLAlchemyError)
    async def db_error(request: Request, exc: SQLAlchemyError):
        log.error("database error=%s", type(exc).__name__)
        return _reply(503, "Database is temporarily unavailable")

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        log.error("unexpected error=%s", type(exc).__name__)
        return _reply(500, "Internal server error")
