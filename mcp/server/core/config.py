"""Application configuration helpers for DB connectivity."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / ".env"
# Load environment variables from .env when present
load_dotenv(dotenv_path=_ENV_PATH, override=False)


class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing."""


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    schema: Optional[str] = None


@dataclass(frozen=True)
class Settings:
    knowledge_db: DatabaseConfig
    auth_db: DatabaseConfig
    policy_db: DatabaseConfig
    # AI/Search Settings
    google_api_key: Optional[str]
    google_search_key: Optional[str]
    google_cx_id: Optional[str]
    model_name: str
    model_name: str
    scraper_service_enabled: bool
    scraper_service_base_url: Optional[str]
    scraper_service_timeout: int


_settings: Optional[Settings] = None


def _require(env_var: str) -> str:
    value = os.getenv(env_var)
    if not value:
        raise ConfigurationError(f"Missing environment variable: {env_var}")
    return value


def _build_db_config(prefix: str, *, include_schema: bool = False) -> DatabaseConfig:
    host = _require(f"{prefix}_HOST")
    port_raw = _require(f"{prefix}_PORT")
    name = _require(f"{prefix}_NAME")
    user = _require(f"{prefix}_USER")
    password = _require(f"{prefix}_PASSWORD")

    schema = None
    if include_schema:
        schema = os.getenv(f"{prefix}_SCHEMA")

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ConfigurationError(
            f"Invalid integer for {prefix}_PORT: {port_raw}"
        ) from exc

    return DatabaseConfig(
        host=host,
        port=port,
        name=name,
        user=user,
        password=password,
        schema=schema,
    )


def _build_settings() -> Settings:
    return Settings(
        knowledge_db=_build_db_config("KNOWLEDGE_DB", include_schema=True),
        auth_db=_build_db_config("AUTH_DB"),
        policy_db=_build_db_config("POLICY_DB"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_search_key=os.getenv("GOOGLE_SEARCH_KEY"),
        google_cx_id=os.getenv("GOOGLE_CX_ID"),
        model_name=os.getenv("MODEL_NAME", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"),
        scraper_service_enabled=os.getenv("SCRAPER_SERVICE_ENABLED", "false").lower() == "true",
        scraper_service_base_url=os.getenv("SCRAPER_SERVICE_BASE_URL"),
        scraper_service_timeout=int(os.getenv("SCRAPER_SERVICE_TIMEOUT", "30")),
    )


def get_settings() -> Settings:
    """Return cached settings, building them if necessary."""

    global _settings
    if _settings is None:
        _settings = _build_settings()
    return _settings


def validate() -> Settings:
    """Validate and return the loaded settings."""

    return get_settings()


__all__ = [
    "ConfigurationError",
    "DatabaseConfig",
    "Settings",
    "get_settings",
    "validate",
]
