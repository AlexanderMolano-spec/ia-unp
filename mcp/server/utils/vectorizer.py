import sys
import os
import numpy as np
from typing import List, Optional, Any
from sentence_transformers import SentenceTransformer

# --- AJUSTE DINAMICO DE IMPORTACIONES ---
# Localiza el directorio 'core' relativo a 'tools'
current_dir = os.path.dirname(os.path.abspath(__file__))
aqua_root = os.path.dirname(current_dir) # Subir un nivel a 'Aqua'
core_path = os.path.join(aqua_root, 'core')

if aqua_root not in sys.path:
    sys.path.append(aqua_root)
if core_path not in sys.path:
    sys.path.append(core_path)

try:
    from utils.config import Config
except ImportError:
    from config import Config

class Vectorizer:
    """
    Herramienta de Vectorización Semántica Local.
    
    Genera embeddings utilizando modelos Transformer locales via sentence-transformers.
    Configurada para alta dimensionalidad (768d).
    
    Atributos:
        model_name (str): Identificador del modelo en HuggingFace.
        model (SentenceTransformer): Instancia del modelo cargado en memoria RAM.
    """

    def __init__(self):
        """
        Inicializa la herramienta y carga el modelo en memoria.
        
        Modelo seleccionado: 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        Características:
            - Multilingüe (Soporte nativo Español/Inglés).
            - Dimensiones: 768 (Alta densidad semántica).
            - Ejecución: Local (CPU/GPU), sin dependencia de APIs externas.
        """
        # Usa el valor de config o el fallback al modelo específico de 768d
        self.model_name = getattr(Config, 'MODELO_EMBEDDING', 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        self.model = None
        self._cargar_modelo()

    def _cargar_modelo(self) -> None:
        """
        Carga el modelo de IA en memoria RAM.
        Maneja excepciones para evitar la interrupción del servicio principal.
        """
        try:
            print(f"[INFO] Cargando modelo de vectorización: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print("[INFO] Modelo cargado exitosamente.")
        except Exception as e:
            print(f"[ERROR CRITICO] Fallo al cargar el modelo de vectorización: {e}", file=sys.stderr)
            self.model = None

    def generar_embedding(self, texto: str) -> Optional[List[float]]:
        """
        Genera una representación vectorial (embedding) para el texto proporcionado.

        Args:
            texto (str): El fragmento de texto o documento a procesar.

        Returns:
            List[float]: Lista de 768 números flotantes representando el texto.
                         Retorna None en caso de error.
        """
        if not self.model or not texto:
            return None
        
        try:
            # Generación del vector
            embedding = self.model.encode(texto)
            
            # Conversión de tipos: Numpy Array -> Lista Python estándar para serialización JSON
            if isinstance(embedding, np.ndarray):
                return embedding.tolist()
            
            return embedding
            
        except Exception as e:
            print(f"[ERROR IA] Fallo durante la generación del embedding: {e}", file=sys.stderr)
            return None

# Instancia global exportada
vectorizer_engine = Vectorizer()