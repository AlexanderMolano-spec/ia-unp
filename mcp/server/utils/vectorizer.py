import sys
import os
import numpy as np
from typing import List, Optional, Any
from sentence_transformers import SentenceTransformer

# --- AJUSTE DINAMICO DE RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
server_root = os.path.dirname(current_dir)

if server_root not in sys.path:
    sys.path.append(server_root)

# Importamos la configuracion desde utils ahora
from utils.config import get_app_settings

class Vectorizer:
    """Motor de Vectorizacion Semantica Local.

    Utiliza modelos de Sentence Transformers para transformar texto en arreglos
    numericos (embeddings) que permiten la busqueda por similitud semantica.

    Attributes:
        model_name (str): Nombre del modelo cargado desde la configuracion.
        model (SentenceTransformer): Instancia activa del modelo.
    """

    def __init__(self):
        """Inicializa el vectorizador cargando el modelo configurado."""
        settings = get_app_settings()
        self.model_name = settings.model_name
        self.model = None
        self._cargar_modelo()

    def _cargar_modelo(self) -> None:
        """Carga el modelo de Transformers en memoria.

        Raises:
            Exception: Si el modelo no puede ser descargado o instanciado.
        """
        try:
            print(f"INFO: [IA] Cargando modelo de vectorizacion: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print("SUCCESS: [IA] Modelo cargado exitosamente.")
        except Exception as e:
            print(f"ERROR: [IA] Fallo al cargar el modelo de vectorizacion: {e}", file=sys.stderr)
            self.model = None

    def generar_embedding(self, texto: str) -> Optional[List[float]]:
        """Genera un vector numerico a partir de una cadena de texto.

        Args:
            texto: El contenido textual a vectorizar.

        Returns:
            Optional[List[float]]: Lista de floats representando el embedding o None si falla.
        """
        if not self.model or not texto:
            return None
        
        try:
            embedding = self.model.encode(texto)
            if isinstance(embedding, np.ndarray):
                return embedding.tolist()
            return embedding
        except Exception as e:
            print(f"ERROR: [IA] Fallo durante la generacion del embedding: {e}", file=sys.stderr)
            return None

# Instancia global exportada para uso compartido del modelo en memoria
vectorizer_engine = Vectorizer()