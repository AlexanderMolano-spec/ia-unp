"""Knowledge DB connector helpers."""
from __future__ import annotations

from typing import Any, Dict

import psycopg
from psycopg import Connection

from core.config import DatabaseConfig, get_settings


def _connection_kwargs(cfg: DatabaseConfig) -> Dict[str, Any]:
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


def get_connection() -> Connection:
    """Return a new connection to the Knowledge DB."""

    cfg = get_settings().knowledge_db
    return psycopg.connect(**_connection_kwargs(cfg))


__all__ = ["get_connection"]
