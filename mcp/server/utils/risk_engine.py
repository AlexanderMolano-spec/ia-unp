import sys
import os
from typing import Dict, Any, List

# --- CONFIGURACION DE RUTAS E IMPORTACIONES ---
# Localiza el directorio raiz del servidor 'Aqua' para importar modulos internos
current_dir = os.path.dirname(os.path.abspath(__file__))
aqua_root = os.path.dirname(current_dir)

if aqua_root not in sys.path:
    sys.path.append(aqua_root)

try:
    # Importacion de dependencias internas corregidas (sin 'src')
    from utils.db import db_engine
    from utils.vectorizer import vectorizer_engine
except ImportError as e:
    print(f"[FATAL] RiskEngine: Error importando dependencias: {e}", file=sys.stderr)
    # Se definen como None para evitar crash inmediato, aunque fallaran al usarse
    db_engine = None
    vectorizer_engine = None

class RiskEngine:
    """
    Motor de Analisis de Riesgos (Cerebro Semantico).
    
    Responsabilidad:
        Recibe texto crudo, lo vectoriza y lo compara semanticamente contra
        la Base de Conocimiento (eco_aqua_base_conocimiento) utilizando
        la distancia coseno proporcionada por la extension pgvector de PostgreSQL.
    """
    
    # Umbral de Similitud (Distance Threshold)
    # En pgvector usando el operador de coseno (<=>):
    # 0.0 significa vectores identicos (misma direccion).
    # 1.0 significa vectores ortogonales (sin relacion).
    # Un valor < 0.45 indica una similitud semantica fuerte para el modelo mpnet-base-v2.
    UMBRAL_ALERTA = 0.45 

    def analizar_fragmento(self, texto_fragmento: str) -> Dict[str, Any]:
        """
        Ejecuta el analisis semantico de un fragmento de texto contra la base de conocimiento.
        
        Args:
            texto_fragmento (str): El texto a analizar.
            
        Returns:
            Dict: Estructura con el resultado del analisis:
                  {
                      "es_riesgo": bool,
                      "etiqueta": str (Ej. 'Amenaza', 'Atentado', 'Sin Riesgo'),
                      "confianza": float (0.0 a 1.0),
                      "evidencia": str (El texto de referencia encontrado en BD)
                  }
        """
        # Estructura de respuesta por defecto (Resultado Negativo)
        resultado = {
            "es_riesgo": False,
            "etiqueta": "Sin Riesgo",
            "confianza": 0.0,
            "evidencia": None
        }

        # Validacion de dependencias
        if not vectorizer_engine or not db_engine:
            print("[ERROR] RiskEngine: Dependencias (DB o Vectorizer) no inicializadas.", file=sys.stderr)
            return resultado

        # 1. Vectorizacion del input
        # Convertimos el texto entrante en un array de 768 dimensiones
        vector = vectorizer_engine.generar_embedding(texto_fragmento)
        
        if not vector:
            # Si el texto es vacio o falla el modelo, retornamos negativo
            return resultado

        conn = db_engine.get_connection()
        if not conn:
            return resultado

        try:
            cur = conn.cursor()
            
            # 2. Busqueda de Vecinos Mas Cercanos (KNN Search)
            # Buscamos el registro mas similar en la tabla eco_aqua_base_conocimiento.
            # El operador <=> calcula la distancia coseno entre el vector input y los almacenados.
            # Ordenamos por distancia ascendente (menor distancia = mayor similitud) y tomamos el mejor (LIMIT 1).
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
            
            # Convertimos la lista de floats a string para que psycopg2 la adapte al tipo vector de PG
            cur.execute(query, (str(vector),))
            match = cur.fetchone()
            
            if match:
                etiqueta_detectada, evidencia_encontrada, distancia = match
                
                # 3. Evaluacion del Riesgo segun Umbral
                # Si la distancia es menor al umbral, consideramos que hay una coincidencia valida.
                if distancia < self.UMBRAL_ALERTA:
                    
                    # Convertimos la distancia inversa en un porcentaje de confianza legible (0 a 1)
                    confianza = round(1.0 - float(distancia), 4)
                    
                    # Logica de Negocio:
                    # Filtramos etiquetas que, aunque coincidan, no representan un riesgo de seguridad.
                    # Ej: Si la base de conocimiento tiene ejemplos de 'Ruido' o 'Salud', no activamos la alerta.
                    etiquetas_ignorar = ["Sin Riesgo", "Ruido", "Salud", "General"]
                    es_positivo = etiqueta_detectada not in etiquetas_ignorar
                    
                    resultado["es_riesgo"] = es_positivo
                    resultado["etiqueta"] = etiqueta_detectada
                    resultado["confianza"] = confianza
                    resultado["evidencia"] = evidencia_encontrada
            
            cur.close()
            # No cerramos la conexion aqui si se planea usar pool, pero db.return_connection no esta en este scope.
            # Se asume que el connection handler maneja el cierre o retorno.
            conn.close() 

        except Exception as e:
            print(f"[ERROR] Excepcion en motor de riesgos: {e}", file=sys.stderr)
            if conn: 
                try:
                    conn.close()
                except:
                    pass

        return resultado

# Instancia global exportada
risk_engine = RiskEngine()