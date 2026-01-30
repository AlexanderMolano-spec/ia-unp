"""Application configuration for external APIs and AI models."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Configuración de base de directorio para carga de .env
_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing."""
    pass

@dataclass(frozen=True)
class AppConfig:
    """Configuración general de la aplicación (Google, AI, Scraper)."""
    google_api_key: Optional[str]
    google_search_key: Optional[str]
    google_cx_id: Optional[str]
    model_name: str
    scraper_service_enabled: bool
    scraper_service_base_url: Optional[str]
    scraper_service_timeout: int

_app_settings: Optional[AppConfig] = None

def _require(env_var: str) -> str:
    """Valida que una variable de entorno exista.

    Args:
        env_var: Nombre de la variable de entorno.

    Returns:
        str: El valor de la variable.

    Raises:
        ConfigurationError: Si la variable no está definida.
    """
    value = os.getenv(env_var)
    if not value:
        raise ConfigurationError(f"Missing environment variable: {env_var}")
    return value

def _build_app_settings() -> AppConfig:
    """Construye la instancia de AppConfig desde el entorno.

    Returns:
        AppConfig: Instancia con los valores cargados.
    """
    return AppConfig(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_search_key=os.getenv("GOOGLE_SEARCH_KEY"),
        google_cx_id=os.getenv("GOOGLE_CX_ID"),
        model_name=os.getenv("MODEL_NAME", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"),
        scraper_service_enabled=os.getenv("SCRAPER_SERVICE_ENABLED", "false").lower() == "true",
        scraper_service_base_url=os.getenv("SCRAPER_SERVICE_BASE_URL"),
        scraper_service_timeout=int(os.getenv("SCRAPER_SERVICE_TIMEOUT", "30")),
    )

def get_app_settings() -> AppConfig:
    """Retorna la configuración de la aplicación (singleton).

    Returns:
        AppConfig: La configuración cargada.
    """
    global _app_settings
    if _app_settings is None:
        _app_settings = _build_app_settings()
    return _app_settings
