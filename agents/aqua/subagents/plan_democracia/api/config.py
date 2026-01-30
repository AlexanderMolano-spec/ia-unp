"""Configuration loader for the AQUA/Plan Democracia subagent."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def _load_env_file() -> None:
    """Search upwards for a .env file (repo root) and load it if present."""

    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            return
    # Fallback to default behaviour (search current working directory)
    load_dotenv(override=False)


_load_env_file()


def _to_bool(value: Optional[str], *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    debug: bool
    gemini_api_key: str
    gemini_model: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    debug = _to_bool(os.getenv("DEBUG"), default=False)
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    if not api_key and not debug:
        raise RuntimeError(
            "GEMINI_API_KEY must be configured when DEBUG is false"
        )

    return Settings(debug=debug, gemini_api_key=api_key, gemini_model=model)


__all__ = ["Settings", "get_settings"]
