import os
import sys
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """
    Configuracion centralizada del sistema Aqua.
    """
    # Base de Datos
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "knowledge_db")
    #DB_NAME: str = os.getenv("DB_NAME", "mcp-unp-db")
    
    _pass: Optional[str] = os.getenv("DB_PASS")
    DB_PASS: Optional[str] = _pass.strip('"') if _pass else None

    # Modelos IA (768d)
    # Intenta 'MODEL_NAME' primero (según .env nuevo) o 'MODELO_EMBEDDING'
    MODELO_EMBEDDING: str = os.getenv(
        "MODEL_NAME", 
        os.getenv("MODELO_EMBEDDING", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    )

    # APIs
    API_KEY_SEARCH: Optional[str] = os.getenv("GOOGLE_SEARCH_KEY")
    SEARCH_ENGINE_ID: Optional[str] = os.getenv("GOOGLE_CX_ID")
    GEMINI_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")

    @staticmethod
    def validate() -> None:
        if not Config.DB_PASS:
            print("[ERROR CONFIG] DB_PASS no configurado.", file=sys.stderr)

Config.validate()