"""Policy DB connector helpers."""
from __future__ import annotations

import psycopg
from psycopg import Connection

from core.db.config import get_policy_db_connection_kwargs


def get_connection() -> Connection:
    """Return a new connection to the Policy DB."""

    return psycopg.connect(**get_policy_db_connection_kwargs())


__all__ = ["get_connection"]
