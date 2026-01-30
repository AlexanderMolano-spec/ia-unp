import os
import sys
import google.generativeai as genai
from typing import List, Dict, Any

# Importamos la nueva configuración y el conector de la base de datos desde core
from core.config import get_settings
from utils.config import get_app_settings
from core.db.knowledge import get_connection

# ---------------------------------------------------------
# CONFIGURACION DEL MODELO GENERATIVO
# ---------------------------------------------------------
# Se obtienen los settings centralizados (AppConfig para IA)
app_settings = get_app_settings()
genai.configure(api_key=app_settings.google_api_key)

def logic_consultar_conocimiento(pregunta: str) -> str:
    """Motor de Analisis NL2SQL (Natural Language to SQL).

    Traduce preguntas de lenguaje natural a consultas SQL ejecutables sobre el
    esquema de la base de datos de conocimiento de la UNP, utilizando el modelo
    Gemini para la generacion del codigo.

    Args:
        pregunta: La consulta en lenguaje natural realizada por el usuario.

    Returns:
        Una cadena con los resultados de la consulta formateados en una tabla
        o un mensaje de error descriptivo en caso de fallo.

    Raises:
        Exception: Si ocurre un error critico no manejado durante el proceso.
    """
    try:
        # 1. CARGA DE CONTEXTO (Diccionario de Datos)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_root = os.path.dirname(os.path.dirname(current_dir))
        dict_path = os.path.join(server_root, "resources", "data_dictionary.md")
        
        if not os.path.exists(dict_path):
            return "ERROR CONFIG: No se encontro el archivo 'data_dictionary.md' en la carpeta resources."

        with open(dict_path, 'r', encoding='utf-8') as f:
            diccionario_contenido = f.read()

        # 2. INGENIERIA DE PROMPT (Generacion de SQL)
        prompt = f"""
Eres un arquitecto de datos experto en PostgreSQL. Tu objetivo es traducir preguntas de lenguaje natural a código SQL ejecutable y optimizado.

CONTEXTO DEL ESQUEMA (Tablas y Relaciones):
{diccionario_contenido}

REGLAS DE GENERACIÓN:
1. Retorna EXCLUSIVAMENTE el código SQL. Sin bloques de markdown (```), sin explicaciones y sin saludos.
2. Usa sintaxis válida de PostgreSQL.
3. Para búsquedas de similitud semántica, utiliza los operadores de la extensión pgvector (como <=>) si es pertinente.

PREGUNTA DEL USUARIO:
"{pregunta}"

SQL RESULTANTE:"""

        # 3. INTERACCION CON LLM (Gemini)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        sql_query = response.text.strip().replace('```sql', '').replace('```', '').strip()

        if not sql_query.lower().startswith("select"):
             return f"WARNING: La consulta generada no parece ser de lectura. Por seguridad se cancelo.\nSQL Generado: {sql_query}"

        # 4. EJECUCION EN BASE DE DATOS
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return "ERROR DB: No se pudo establecer conexion con la base de datos."
                
            resultados = []
            colnames = []

            cur = conn.cursor()
            cur.execute(sql_query)
            
            if cur.description:
                colnames = [desc[0] for desc in cur.description]
                resultados = cur.fetchall()
            
            cur.close()
        except Exception as query_error:
            return f"ERROR SQL: Fallo en la ejecucion de la consulta:\nDetalle: {query_error}\nQuery: {sql_query}"
        finally:
            if conn:
                conn.close()

        # 5. FORMATEO DE RESPUESTA
        if not resultados:
            return f"INFO: La consulta se ejecuto correctamente pero no arrojo resultados.\nQuery: {sql_query}"

        header = " | ".join(colnames)
        separator = "-" * len(header)
        
        filas_formateadas = []
        for row in resultados:
            filas_formateadas.append(" | ".join(str(val) for val in row))
        
        res_text = [
            "[RESULTADOS DEL ANALISIS]",
            separator,
            header,
            separator
        ]
        res_text.extend(filas_formateadas)
        res_text.append(separator)
        res_text.append(f"[METADATA] SQL Ejecutado: {sql_query}")
        
        return "\n".join(res_text)

    except Exception as e:
        return f"ERROR SISTEMA: Excepcion critica en el modulo de analisis SQL: {str(e)}"
