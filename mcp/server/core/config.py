"""Centralized configuration for the MCP server."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)


class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing or invalid."""


def _require(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise ConfigurationError(f"Missing environment variable: {name}")
    return value


def _require_int(name: str) -> int:
    raw = _require(name)
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"Invalid integer for {name}: {raw}") from exc


def _to_bool(value: Optional[str], *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    user: str
    password: str
    schema: Optional[str] = None


@dataclass(frozen=True)
class ScraperSettings:
    enabled: bool
    host: str
    port: int
    base_url: str
    timeout: int


@dataclass(frozen=True)
class GoogleSearchSettings:
    search_key: str
    cx_id: str
    api_key: str


@dataclass(frozen=True)
class EmbeddingSettings:
    model_name: str


@dataclass(frozen=True)
class MCPSettings:
    knowledge_db: DatabaseSettings
    auth_db: DatabaseSettings
    policy_db: DatabaseSettings
    scraper: ScraperSettings
    google_search: GoogleSearchSettings
    embedding: EmbeddingSettings


def _build_db_settings(prefix: str, *, include_schema: bool = False) -> DatabaseSettings:
    host = _require(f"{prefix}_HOST")
    port = _require_int(f"{prefix}_PORT")
    name = _require(f"{prefix}_NAME")
    user = _require(f"{prefix}_USER")
    password = _require(f"{prefix}_PASSWORD")
    schema = os.getenv(f"{prefix}_SCHEMA") if include_schema else None
    return DatabaseSettings(
        host=host,
        port=port,
        name=name,
        user=user,
        password=password,
        schema=schema,
    )


def _build_scraper_settings() -> ScraperSettings:
    enabled = _to_bool(os.getenv("SCRAPER_SERVICE_ENABLED"), default=False)
    host = os.getenv("SCRAPER_SERVICE_HOST", "")
    port_str = os.getenv("SCRAPER_SERVICE_PORT")
    base_url = os.getenv("SCRAPER_SERVICE_BASE_URL", "")
    timeout_str = os.getenv("SCRAPER_SERVICE_TIMEOUT")

    port = int(port_str) if port_str else 0
    timeout = int(timeout_str) if timeout_str else 0

    if enabled:
        if not host or not port:
            raise ConfigurationError(
                "SCRAPER_SERVICE_HOST/PORT required when scraper enabled"
            )
        if not base_url:
            raise ConfigurationError(
                "SCRAPER_SERVICE_BASE_URL required when scraper enabled"
            )
        if timeout <= 0:
            timeout = 30

    return ScraperSettings(
        enabled=enabled,
        host=host or "",
        port=port,
        base_url=base_url or "",
        timeout=timeout or 0,
    )


def _build_google_settings() -> GoogleSearchSettings:
    return GoogleSearchSettings(
        search_key=os.getenv("GOOGLE_SEARCH_KEY", ""),
        cx_id=os.getenv("GOOGLE_CX_ID", ""),
        api_key=os.getenv("GOOGLE_API_KEY", ""),
    )


def _build_embedding_settings() -> EmbeddingSettings:
    return EmbeddingSettings(
        model_name=os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-large"),
    )


@lru_cache(maxsize=1)
def get_settings() -> MCPSettings:
    return MCPSettings(
        knowledge_db=_build_db_settings("KNOWLEDGE_DB", include_schema=True),
        auth_db=_build_db_settings("AUTH_DB"),
        policy_db=_build_db_settings("POLICY_DB"),
        scraper=_build_scraper_settings(),
        google_search=_build_google_settings(),
        embedding=_build_embedding_settings(),
    )


def validate() -> MCPSettings:
    """Validate and return the loaded settings."""

    return get_settings()


__all__ = [
    "ConfigurationError",
    "DatabaseSettings",
    "ScraperSettings",
    "GoogleSearchSettings",
    "EmbeddingSettings",
    "MCPSettings",
    "get_settings",
    "validate",
]
