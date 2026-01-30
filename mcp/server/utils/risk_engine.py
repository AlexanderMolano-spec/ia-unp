import sys
import os
from typing import Dict, Any, List

# --- CONFIGURACION DE RUTAS E IMPORTACIONES ---
current_dir = os.path.dirname(os.path.abspath(__file__))
server_root = os.path.dirname(current_dir)

if server_root not in sys.path:
    sys.path.append(server_root)

# Importamos desde core y otros servicios de aqua
from core.db.knowledge import get_connection
from utils.vectorizer import vectorizer_engine

class RiskEngine:
    """Motor de Analisis de Riesgos (Cerebro Semantico).

    Esta clase orquesta la deteccion de riesgos semanticos comparando fragmentos
    de texto con una base de conocimiento etiquetada mediante busqueda vectorial.

    Attributes:
        UMBRAL_ALERTA (float): Valor de distancia maxima para considerar un match positivo.
    """
    UMBRAL_ALERTA = 0.45 

    def analizar_fragmento(self, texto_fragmento: str) -> Dict[str, Any]:
        """Analiza un fragmento de texto para detectar riesgos potenciales.

        Genera un embedding del texto y busca el match mas cercano en la base
        de conocimiento de riesgos.

        Args:
            texto_fragmento: El contenido textual a analizar.

        Returns:
            Dict[str, Any]: Un diccionario con:
                - es_riesgo (bool): Si se detecto un riesgo por debajo del umbral.
                - etiqueta (str): El nombre de la categoria de riesgo.
                - confianza (float): Nivel de confianza del analisis (1.0 - distancia).
                - evidencia (str): El texto de referencia que disparo la alerta.
        """
        resultado = {
            "es_riesgo": False,
            "etiqueta": "Sin Riesgo",
            "confianza": 0.0,
            "evidencia": None
        }

        if not vectorizer_engine:
            return resultado

        vector = vectorizer_engine.generar_embedding(texto_fragmento)
        if not vector:
            return resultado

        conn = None
        try:
            conn = get_connection()
            if not conn:
                return resultado
                
            cur = conn.cursor()
            
            # Busqueda de similitud semantica en la base de conocimiento
            query = """
                SELECT 
                    er.nombre as etiqueta,
                    bc.texto as evidencia,
                    (bc.embedding <=> %s) as distancia
                FROM eco_aqua_base_conocimiento bc
                JOIN eco_aqua_etiquetariesgo er ON bc.id_etiquetariesgo = er.id_etiquetariesgo
                ORDER BY distancia ASC
                LIMIT 1;
            """
            
            cur.execute(query, (str(vector),))
            match = cur.fetchone()
            
            if match:
                etiqueta_detectada, evidencia_encontrada, distancia = match
                # El "POR QUE" del umbral: Se calibro para minimizar falsos positivos 
                # en documentos legales extensos.
                if distancia < self.UMBRAL_ALERTA:
                    confianza = round(1.0 - float(distancia), 4)
                    etiquetas_ignorar = ["Sin Riesgo", "Ruido", "Salud", "General"]
                    es_positivo = etiqueta_detectada not in etiquetas_ignorar
                    
                    resultado["es_riesgo"] = es_positivo
                    resultado["etiqueta"] = etiqueta_detectada
                    resultado["confianza"] = confianza
                    resultado["evidencia"] = evidencia_encontrada
            
            cur.close()
        except Exception as e:
            # Salida de error sobria hacia stderr
            print(f"ERROR: Excepcion en motor de riesgos: {e}", file=sys.stderr)
        finally:
            if conn:
                conn.close()

        return resultado

# Instancia global exportada para uso en el sistema
risk_engine = RiskEngine()