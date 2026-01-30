import os
import sys
import google.generativeai as genai
from typing import List, Dict, Any

# Importamos configuracion y conexion
from core.config import get_settings
from utils.config import get_app_settings
from core.db.knowledge import get_connection

# Configuracion de Gemini
app_settings = get_app_settings()
genai.configure(api_key=app_settings.google_api_key)

def logic_reportar_objetivo(objetivo: str) -> str:
    """Genera un informe detallado de un objetivo basado en la informacion de la base de datos.

    Extrae todos los hallazgos y metadatos asociados a un objetivo desde la
    base de datos documental y utiliza Gemini para sintetizar un reporte narrativo
    profesional.

    Args:
        objetivo: El nombre del objetivo para el cual se generara el informe.

    Returns:
        Un informe narrativo completo generado por la IA o un mensaje descriptivo
        si no se encontraron datos.

    Raises:
        Exception: Si ocurre un error en la consulta a BD o en la generacion de contenido.
    """
    try:
        # 1. Obtencion de datos de la base de datos
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return "ERROR DB: No se pudo conectar a la base de datos para generar reporte."
                
            cur = conn.cursor()
            
            # Consulta para extraer toda la informacion vinculada
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
                return f"INFO: No se encontro informacion previa para el objetivo '{objetivo}' en la base de datos."

            # Procesar datos crudos para el prompt
            datos_crudos = []
            info_basica = f"Objetivo: {rows[0][0]}"
            if rows[0][1]: info_basica += f" | Partido/Afiliacion: {rows[0][1]}"
            
            datos_crudos.append(info_basica)
            datos_crudos.append("\n--- HALLAZGOS ---")
            
            for row in rows:
                if row[6]:
                    entry = f"- Fuente: {row[4]} ({row[5]})\n  Hallazgo: {row[6]}"
                    datos_crudos.append(entry)

            datos_crudos_text = "\n\n".join(datos_crudos)
            cur.close()
        finally:
            if conn:
                conn.close()

        # 2. Carga del Template de Prompt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_root = os.path.dirname(os.path.dirname(current_dir))
        prompt_path = os.path.join(server_root, "prompts", "prompt_reporte_objetivo.md")
        
        if not os.path.exists(prompt_path):
            return "ERROR: No se encontro el recurso 'prompt_reporte_objetivo.md'."

        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # 3. Inyeccion de datos y llamado a Gemini
        final_prompt = template.format(
            OBJETIVO=objetivo,
            DATOS_CRUDOS=datos_crudos_text
        )

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(final_prompt)
        
        return response.text

    except Exception as e:
        return f"ERROR SISTEMA: Error al generar el informe: {str(e)}"
