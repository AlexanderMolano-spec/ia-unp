import os
import sys
import json
import google.generativeai as genai
from typing import List, Dict, Any
from utils.config import Config
from utils.db import db_engine
from utils.vectorizer import vectorizer_engine

# Configuración de Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

def logic_evaluar_hechos(objetivo: str) -> str:
    """
    Realiza una auditoría forense sobre los hechos victimizantes detectados para un objetivo.
    """
    try:
        # 0. Localización de recursos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_root = os.path.dirname(os.path.dirname(current_dir))
        prompt_path = os.path.join(server_root, "prompts", "prompt_evaluacion_forense.md")
        
        if not os.path.exists(prompt_path):
            return f"[ERROR] No se encontró el recurso: {prompt_path}"

        with open(prompt_path, 'r', encoding='utf-8') as f:
            template_prompt = f.read()

        # 1. SQL: Buscar fragmentos de alto riesgo para el objetivo
        conn = db_engine.get_connection()
        if not conn:
            return "[ERROR] Sin conexión a la base de datos."

        cur = conn.cursor()
        
        # SQL para traer fragmentos con fatalidad detectada o etiquetas de riesgo
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
            conn.close()
            return f"[AUDITORÍA] No se encontraron hechos de riesgo preliminares para '{objetivo}'."

        ficha_reporte = [f"🛡️ AUDITORÍA FORENSE: {objetivo.upper()}\n"]
        
        # 2 y 3. Radar (Vectorial) y Lupa (Semántica)
        for frag_id, texto, embedding, etiqueta, confianza in hallazgos:
            # --- RADAR (Repetitividad Vectorial) ---
            # Contar fragmentos similares (>90% similitud, distancia < 0.1)
            sql_radar = """
                SELECT COUNT(*) 
                FROM eco_aqua_fragmento_vector 
                WHERE (embedding <=> %s::vector) < 0.1
                  AND id_fragmento != %s;
            """
            cur.execute(sql_radar, (embedding, frag_id))
            repetitividad = cur.fetchone()[0]
            
            # --- LUPA (Análisis de Gemini) ---
            prompt_final = template_prompt.format(TEXTO_HECHO=texto)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            try:
                response = model.generate_content(prompt_final)
                # Intentar limpiar JSON de markdown si existe
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                analisis = json.loads(raw_json)
            except Exception as e:
                analisis = {
                    "denuncia_formal": False,
                    "hecho_publico": False,
                    "evidencia_fisica": f"Error en análisis: {str(e)}",
                    "nivel_credibilidad": 0
                }

            # 4. Consolidación de la Ficha Técnica
            status_denuncia = "✅ FORMALIZADO" if analisis.get("denuncia_formal") else "⚠️ NO FORMALIZADO"
            status_publico = "🌐 PÚBLICO" if analisis.get("hecho_publico") else "🔒 PRIVADO/DISCRETO"
            
            ficha_reporte.append("-" * 50)
            ficha_reporte.append(f"📌 HECHO: {texto[:200]}...")
            ficha_reporte.append(f"🏷️ CATEGORÍA: {etiqueta if etiqueta else 'Riesgo Desconocido'} (Confianza: {confianza:.2f})")
            ficha_reporte.append(f"📡 RADAR (Repetitividad): Se encontró en {repetitividad} otras fuentes.")
            ficha_reporte.append(f"⚖️ ESTATUS: {status_denuncia} | {status_publico}")
            ficha_reporte.append(f"🔍 EVIDENCIAS: {analisis.get('evidencia_fisica')}")
            ficha_reporte.append(f"⭐ CREDIBILIDAD: {analisis.get('nivel_credibilidad')}/10")

        cur.close()
        conn.close()
        
        return "\n".join(ficha_reporte)

    except Exception as e:
        return f"[ERROR FORENSE] {str(e)}"
