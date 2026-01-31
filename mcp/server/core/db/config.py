"""Database connection helpers built from MCP settings."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from core.config import DatabaseSettings, get_settings


def _build_connection_kwargs(cfg: DatabaseSettings) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {
        "host": cfg.host,
        "port": cfg.port,
        "dbname": cfg.name,
        "user": cfg.user,
        "password": cfg.password,
    }
    if cfg.schema:
        kwargs["options"] = f"-c search_path={cfg.schema}"
    return kwargs


def _build_dsn(cfg: DatabaseSettings) -> str:
    return (
        f"postgresql://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.name}"
    )


def get_knowledge_db_connection_kwargs() -> Dict[str, Any]:
    return _build_connection_kwargs(get_settings().knowledge_db)


def get_auth_db_connection_kwargs() -> Dict[str, Any]:
    return _build_connection_kwargs(get_settings().auth_db)


def get_policy_db_connection_kwargs() -> Dict[str, Any]:
    return _build_connection_kwargs(get_settings().policy_db)


def get_knowledge_db_dsn() -> str:
    return _build_dsn(get_settings().knowledge_db)


def get_auth_db_dsn() -> str:
    return _build_dsn(get_settings().auth_db)


def get_policy_db_dsn() -> str:
    return _build_dsn(get_settings().policy_db)


def get_knowledge_db_schema() -> str | None:
    return get_settings().knowledge_db.schema


__all__ = [
    "get_knowledge_db_connection_kwargs",
    "get_auth_db_connection_kwargs",
    "get_policy_db_connection_kwargs",
    "get_knowledge_db_dsn",
    "get_auth_db_dsn",
    "get_policy_db_dsn",
    "get_knowledge_db_schema",
]
