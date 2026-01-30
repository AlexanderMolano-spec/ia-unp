import os
import sys
import google.generativeai as genai
from typing import List, Dict, Any

# Importamos la configuración y el motor de base de datos (Engine)
from utils.config import Config
from utils.db import db_engine

# ---------------------------------------------------------
# CONFIGURACIÓN DEL MODELO GENERATIVO
# ---------------------------------------------------------
# Se inicializa el cliente de Gemini con la API Key específica para IA.
genai.configure(api_key=Config.GEMINI_API_KEY)

def logic_consultar_conocimiento(pregunta: str) -> str:
    """
    Motor de Análisis NL2SQL (Natural Language to SQL).
    
    Flujo de ejecución:
    1. Carga el esquema de la base de datos (Diccionario de Datos).
    2. Envía el esquema y la pregunta del usuario al LLM (Gemini).
    3. Obtiene y limpia el código SQL generado.
    4. Ejecuta la consulta en la base de datos PostgreSQL.
    5. Formatea los resultados en una tabla de texto plano.
    """
    try:
        # ---------------------------------------------------------
        # 1. CARGA DE CONTEXTO (Diccionario de Datos)
        # ---------------------------------------------------------
        # Obtenemos la ruta del directorio actual (tools/aqua/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Subimos dos niveles para llegar a la raíz del servidor (mcp/server/)
        # tools/aqua/ -> tools/ -> server/
        server_root = os.path.dirname(os.path.dirname(current_dir))
        dict_path = os.path.join(server_root, "resources", "data_dictionary.md")
        
        # Validación de existencia del recurso
        if not os.path.exists(dict_path):
            return "[ERROR CONFIG] No se encontró el archivo 'data_dictionary.md' en la carpeta resources."

        with open(dict_path, 'r', encoding='utf-8') as f:
            diccionario_contenido = f.read()

        # ---------------------------------------------------------
        # 2. INGENIERÍA DE PROMPT (Generación de SQL)
        # ---------------------------------------------------------
        prompt = f"""
Eres un arquitecto de datos experto en PostgreSQL. Tu objetivo es traducir preguntas de lenguaje natural a código SQL ejecutable y optimizado.

CONTEXTO DEL ESQUEMA (Tablas y Relaciones):
{diccionario_contenido}

REGLAS DE GENERACIÓN:
1. Retorna EXCLUSIVAMENTE el código SQL. Sin bloques de markdown (```), sin explicaciones y sin saludos.
2. Usa sintaxis válida de PostgreSQL.
3. Para búsquedas de similitud semántica, utiliza los operadores de la extensión pgvector (como <=>) si es pertinente.
4. Si la pregunta es ambigua, genera la consulta más lógica basada en los nombres de las tablas.

PREGUNTA DEL USUARIO:
"{pregunta}"

SQL RESULTANTE:"""

        # ---------------------------------------------------------
        # 3. INTERACCIÓN CON LLM (Gemini)
        # ---------------------------------------------------------
        # Usamos el modelo flash por velocidad y eficiencia en tareas de código
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Limpieza robusta de la respuesta (eliminar formateo markdown si el modelo lo incluye)
        sql_query = response.text.strip().replace('```sql', '').replace('```', '').strip()

        # Validación de seguridad básica: Solo permitir consultas de lectura (SELECT)
        if not sql_query.lower().startswith("select"):
             return f"[ADVERTENCIA] La consulta generada no parece ser de lectura. Por seguridad se canceló.\nSQL Generado: {sql_query}"

        # ---------------------------------------------------------
        # 4. EJECUCIÓN EN BASE DE DATOS
        # ---------------------------------------------------------
        conn = db_engine.get_connection()
        if not conn:
            return "[ERROR CONEXION] No hay conexión activa con la base de datos."

        resultados = []
        colnames = []

        try:
            cur = conn.cursor()
            cur.execute(sql_query)
            
            # Si la consulta devuelve datos, extraemos encabezados y filas
            if cur.description:
                colnames = [desc[0] for desc in cur.description]
                resultados = cur.fetchall()
            
            cur.close()
            conn.close()
        except Exception as query_error:
            # Cierre seguro de conexión en caso de error SQL
            if conn: conn.close()
            return f"[ERROR SQL] Fallo en la ejecución de la consulta:\nDetalle: {query_error}\nQuery: {sql_query}"

        # ---------------------------------------------------------
        # 5. FORMATEO DE RESPUESTA
        # ---------------------------------------------------------
        if not resultados:
            return f"[INFO] La consulta se ejecutó correctamente pero no arrojó resultados.\nQuery: {sql_query}"

        # Construcción de tabla en texto plano para el usuario
        header = " | ".join(colnames)
        separator = "-" * len(header) # Línea divisoria basada en la longitud del header
        
        filas_formateadas = []
        for row in resultados:
            # Convertimos todos los valores a string para evitar errores de concatenación
            filas_formateadas.append(" | ".join(str(val) for val in row))
        
        # Ensamble del reporte final
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
        return f"[ERROR SISTEMA] Excepción crítica en el módulo de análisis SQL: {str(e)}"
