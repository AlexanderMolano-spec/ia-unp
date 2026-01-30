import os
import sys
import google.generativeai as genai
from typing import List, Dict, Any
from utils.config import Config
from utils.db import db_engine

# Configuración de Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

def logic_reportar_objetivo(objetivo: str) -> str:
    """
    Genera un informe detallado de un objetivo basado en la información de la base de datos.
    """
    try:
        # 1. Obtención de datos de la base de datos
        conn = db_engine.get_connection()
        if not conn:
            return "[ERROR] No hay conexión activa con la base de datos."

        cur = conn.cursor()
        
        # Consulta para extraer toda la información vinculada
        sql = """
            SELECT 
                o.nombre as objetivo,
                o.partido,
                c.consulta as termino_busqueda,
                c.fecha_inicio,
                d.titulo as documento_titulo,
                d.url as fuente_url,
                f.texto_fragmento
            FROM eco_aqua_objetivo_busqueda o
            LEFT JOIN eco_aqua_ejecucionconsulta c ON o.id_objetivo = c.id_objetivo
            LEFT JOIN eco_aqua_documento d ON c.id_ejecucionconsulta = d.id_ejecucionconsulta
            LEFT JOIN eco_aqua_fragmento f ON d.id_documento = f.id_documento
            WHERE o.nombre ILIKE %s
            ORDER BY c.fecha_inicio DESC, f.nro_secuencia ASC;
        """
        
        cur.execute(sql, (f"%{objetivo}%",))
        rows = cur.fetchall()
        
        if not rows:
            cur.close()
            conn.close()
            return f"[INFO] No se encontró información previa para el objetivo '{objetivo}' en la base de datos."

        # Procesar datos crudos para el prompt
        datos_crudos = []
        info_basica = f"Objetivo: {rows[0][0]}"
        if rows[0][1]: info_basica += f" | Partido/Afiliación: {rows[0][1]}"
        
        datos_crudos.append(info_basica)
        datos_crudos.append("\n--- HALLAZGOS ---")
        
        for row in rows:
            # Evitar fragmentos vacios si hay joins incompletos
            if row[6]:
                entry = f"- Fuente: {row[4]} ({row[5]})\n  Hallazgo: {row[6]}"
                datos_crudos.append(entry)

        datos_crudos_text = "\n\n".join(datos_crudos)
        
        cur.close()
        conn.close()

        # 2. Carga del Template de Prompt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_root = os.path.dirname(os.path.dirname(current_dir))
        prompt_path = os.path.join(server_root, "prompts", "prompt_reporte_objetivo.md")
        
        if not os.path.exists(prompt_path):
            return "[ERROR] No se encontró el recurso 'prompt_reporte_objetivo.md'."

        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # 3. Inyección de datos y llamado a Gemini
        final_prompt = template.format(
            OBJETIVO=objetivo,
            DATOS_CRUDOS=datos_crudos_text
        )

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(final_prompt)
        
        return response.text

    except Exception as e:
        return f"[ERROR SISTEMA] Error al generar el informe: {str(e)}"
