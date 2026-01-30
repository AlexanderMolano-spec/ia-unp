"""Policy DB connector helpers."""
from __future__ import annotations

import psycopg
from psycopg import Connection

from core.config import DatabaseConfig, get_settings


def _connection_kwargs(cfg: DatabaseConfig) -> dict:
    return {
        "host": cfg.host,
        "port": cfg.port,
        "dbname": cfg.name,
        "user": cfg.user,
        "password": cfg.password,
    }


def get_connection() -> Connection:
    """Return a new connection to the Policy DB."""

    cfg = get_settings().policy_db
    return psycopg.connect(**_connection_kwargs(cfg))


__all__ = ["get_connection"]
