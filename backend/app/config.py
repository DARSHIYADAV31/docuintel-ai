from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"  # project root, any cwd


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    gemini_api_key: str = ""
    mistral_api_key: str = ""
    database_url: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    max_upload_mb: int = 20
    llm_timeout_seconds: int = 30
    ocr_timeout_seconds: int = 180
    vector_store: str = "faiss"
    embedding_backend: str = "gemini"  # "gemini" or "local" (Sentence Transformers)
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_model: str = "all-MiniLM-L6-v2"  # local backend: name, or a folder path
    embedding_timeout_seconds: int = 90
    log_level: str = "INFO"
    api_base_url: str = "http://localhost:8000"
    gemini_model: str = "gemini-2.5-flash"
    mistral_model: str = "mistral-small-latest"


@lru_cache
def get_settings() -> Settings:
    return Settings()
