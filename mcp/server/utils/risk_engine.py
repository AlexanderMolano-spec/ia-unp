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
    """
    Motor de Analisis de Riesgos (Cerebro Semantico).
    """
    UMBRAL_ALERTA = 0.45 

    def analizar_fragmento(self, texto_fragmento: str) -> Dict[str, Any]:
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
            cur = conn.cursor()
            
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
            print(f"[ERROR] Excepcion en motor de riesgos: {e}", file=sys.stderr)
        finally:
            if conn:
                conn.close()

        return resultado

# Instancia global exportada
risk_engine = RiskEngine()