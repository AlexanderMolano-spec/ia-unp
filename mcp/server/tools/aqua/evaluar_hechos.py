import os
import sys
import json
import google.generativeai as genai
from typing import List, Dict, Any

# Importamos desde core
from core.config import get_settings
from core.db.knowledge import get_connection
from utils.vectorizer import vectorizer_engine

# Configuracion de Gemini desde settings centralizados
settings = get_settings()
genai.configure(api_key=settings.google_api_key)

def logic_evaluar_hechos(objetivo: str) -> str:
    """Realiza una auditoria forense sobre los hechos victimizantes detectados para un objetivo.

    Analiza fragmentos de texto asociados a un objetivo de busqueda para detectar
    riesgos, repetitividad y credibilidad de los hechos reportados utilizando
    busqueda vectorial y el modelo Gemini.

    Args:
        objetivo: El nombre del objetivo a evaluar (ej. una persona o entidad).

    Returns:
        Una ficha tecnica de auditoria forense formateada en texto plano o un
        mensaje indicando la ausencia de hallazgos.

    Raises:
        Exception: Si ocurre un error critico durante el analisis o la conexion a BD.
    """
    try:
        # 0. Localizacion de recursos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_root = os.path.dirname(os.path.dirname(current_dir))
        prompt_path = os.path.join(server_root, "prompts", "prompt_evaluacion_forense.md")
        
        if not os.path.exists(prompt_path):
            return f"ERROR: No se encontro el recurso: {prompt_path}"

        with open(prompt_path, 'r', encoding='utf-8') as f:
            template_prompt = f.read()

        # 1. SQL: Buscar fragmentos de alto riesgo para el objetivo
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return "ERROR DB: No se pudo conectar a la base de datos."
                
            cur = conn.cursor()
            
            sql_hallazgos = """
                SELECT 
                    f.id_fragmento,
                    f.texto_fragmento,
                    fv.embedding,
                    er.nombre as etiqueta_riesgo,
                    fv.confianza
                FROM eco_aqua_objetivo_busqueda o
                JOIN eco_aqua_ejecucionconsulta c ON o.id_objetivo = c.id_objetivo
                JOIN eco_aqua_documento d ON c.id_ejecucionconsulta = d.id_ejecucionconsulta
                JOIN eco_aqua_fragmento f ON d.id_documento = f.id_documento
                JOIN eco_aqua_fragmento_vector fv ON f.id_fragmento = fv.id_fragmento
                LEFT JOIN eco_aqua_etiquetariesgo er ON fv.id_etiquetariesgo = er.id_etiquetariesgo
                WHERE o.nombre ILIKE %s 
                  AND (fv.fatalidad_detectada = true OR fv.id_etiquetariesgo IS NOT NULL)
                ORDER BY fv.fecha_analisis DESC
                LIMIT 5;
            """
            
            cur.execute(sql_hallazgos, (f"%{objetivo}%",))
            hallazgos = cur.fetchall()
            
            if not hallazgos:
                cur.close()
                return f"INFO: [AUDITORIA] No se encontraron hechos de riesgo preliminares para '{objetivo}'."

            ficha_reporte = [f"INFO: [AUDITORIA FORENSE] {objetivo.upper()}\n"]
            
            # 2 y 3. Radar (Vectorial) y Lupa (Semantica)
            for frag_id, texto, embedding, etiqueta, confianza in hallazgos:
                # --- RADAR (Repetitividad Vectorial) ---
                sql_radar = """
                    SELECT COUNT(*) 
                    FROM eco_aqua_fragmento_vector 
                    WHERE (embedding <=> %s::vector) < 0.1
                      AND id_fragmento != %s;
                """
                cur.execute(sql_radar, (embedding, frag_id))
                repetitividad = cur.fetchone()[0]
                
                # --- LUPA (Analisis de Gemini) ---
                prompt_final = template_prompt.format(TEXTO_HECHO=texto)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                try:
                    response = model.generate_content(prompt_final)
                    raw_json = response.text.replace('```json', '').replace('```', '').strip()
                    analisis = json.loads(raw_json)
                except Exception as e:
                    analisis = {
                        "denuncia_formal": False,
                        "hecho_publico": False,
                        "evidencia_fisica": f"Error en analisis: {str(e)}",
                        "nivel_credibilidad": 0
                    }

                # 4. Consolidacion de la Ficha Tecnica
                status_denuncia = "SUCCESS: [FORMALIZADO]" if analisis.get("denuncia_formal") else "WARNING: [NO FORMALIZADO]"
                status_publico = "INFO: [PUBLICO]" if analisis.get("hecho_publico") else "INFO: [PRIVADO/DISCRETO]"
                
                ficha_reporte.append("-" * 50)
                ficha_reporte.append(f"INFO: [MARK] HECHO: {texto[:200]}...")
                ficha_reporte.append(f"INFO: [TAG] CATEGORIA: {etiqueta if etiqueta else 'Riesgo Desconocido'} (Confianza: {confianza:.2f})")
                ficha_reporte.append(f"INFO: [RADAR] Repetitividad: Se encontro en {repetitividad} otras fuentes.")
                ficha_reporte.append(f"STATUS: {status_denuncia} | {status_publico}")
                ficha_reporte.append(f"INFO: [EVIDENCE] EVIDENCIAS: {analisis.get('evidencia_fisica')}")
                ficha_reporte.append(f"INFO: [QUALITY] CREDIBILIDAD: {analisis.get('nivel_credibilidad')}/10")

            cur.close()
            return "\n".join(ficha_reporte)

        finally:
            if conn:
                conn.close()

    except Exception as e:
        return f"ERROR FORENSE: {str(e)}"
