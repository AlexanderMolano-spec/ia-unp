import sys
import os
import numpy as np
from typing import List, Optional, Any
from sentence_transformers import SentenceTransformer

# --- AJUSTE DINAMICO DE IMPORTACIONES ---
current_dir = os.path.dirname(os.path.abspath(__file__))
server_root = os.path.dirname(current_dir)

if server_root not in sys.path:
    sys.path.append(server_root)

# Importamos la configuración desde core
from core.config import get_settings

class Vectorizer:
    """
    Herramienta de Vectorización Semántica Local usando la configuración de core.
    """

    def __init__(self):
        settings = get_settings()
        self.model_name = settings.model_name
        self.model = None
        self._cargar_modelo()

    def _cargar_modelo(self) -> None:
        try:
            print(f"[INFO] Cargando modelo de vectorización: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print("[INFO] Modelo cargado exitosamente.")
        except Exception as e:
            print(f"[ERROR CRITICO] Fallo al cargar el modelo de vectorización: {e}", file=sys.stderr)
            self.model = None

    def generar_embedding(self, texto: str) -> Optional[List[float]]:
        if not self.model or not texto:
            return None
        
        try:
            embedding = self.model.encode(texto)
            if isinstance(embedding, np.ndarray):
                return embedding.tolist()
            return embedding
        except Exception as e:
            print(f"[ERROR IA] Fallo durante la generación del embedding: {e}", file=sys.stderr)
            return None

# Instancia global exportada
vectorizer_engine = Vectorizer()