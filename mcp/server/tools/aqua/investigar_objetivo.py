import sys
import requests
from typing import List, Tuple

# --- IMPORTACIONES DE TUS UTILIDADES ---
from utils.config import Config
from utils.db import db_engine

# Motores (Servicios)
from utils.scraper import scraper_engine
from utils.text_processor import processor_engine
from utils.vectorizer import vectorizer_engine
from utils.risk_engine import risk_engine
from utils.storage import storage_engine

# --- FUNCIONES PRIVADAS (Helpers) ---

def _buscar_en_google(query: str, logs: List[str]) -> List[str]:
    """Ejecuta búsqueda en Google Custom Search API."""
    if not Config.API_KEY_SEARCH or not Config.SEARCH_ENGINE_ID:
        logs.append("[CONFIG ERROR] Credenciales de Google Search no configuradas.")
        return []
    
    logs.append(f"[BUSQUEDA] Consulta: '{query}'")
    urls = []
    try:
        url_api = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": Config.API_KEY_SEARCH, 
            "cx": Config.SEARCH_ENGINE_ID, 
            "q": query, 
            "num": 5,
            "gl": "co"
        }
        resp = requests.get(url_api, params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "items" in data:
                urls = [item["link"] for item in data["items"]]
                logs.append(f"[BUSQUEDA] Exito: {len(urls)} resultados.")
        else:
            logs.append(f"[BUSQUEDA ERROR] Código API: {resp.status_code}")
            
    except Exception as e:
        logs.append(f"[BUSQUEDA EXCEPCION] {str(e)}")
    return urls

def _parsear_contenido(raw: str) -> Tuple[str, str]:
    """Separa Título y Cuerpo."""
    if not raw: return ("Sin Título", "")
    marker = "CONTENIDO:\n"
    if marker in raw:
        try:
            partes = raw.split("\n\n" + marker, 1)
            titulo = partes[0].replace("TITULO: ", "").strip()
            cuerpo = partes[1].strip()
            return (titulo, cuerpo)
        except: pass
    return ("Titulo Automático", raw.strip())

def _crear_auditoria(target: str, logs: List[str]) -> int:
    """Registra inicio en BD."""
    conn = db_engine.get_connection()
    if not conn:
        logs.append("[DB ERROR] No hay conexión a BD para auditoría.")
        return 0
    
    id_exec = 0
    try:
        cur = conn.cursor()
        sql = """
            INSERT INTO eco_aqua_ejecucionconsulta (consulta, fecha_inicio) 
            VALUES (%s, NOW()) 
            RETURNING id_ejecucionconsulta
        """
        cur.execute(sql, (f"Investigación Aqua: {target}",))
        id_exec = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        logs.append(f"[AUDITORIA] Registro creado ID: {id_exec}")
    except Exception as e:
        logs.append(f"[AUDITORIA ERROR] {e}")
    return id_exec

# --- LÓGICA PRINCIPAL (Solo Investigación) ---

def logic_investigar_objetivo(objetivo: str) -> str:
    """
    Orquesta: Búsqueda -> Scraping -> Guardado -> Vectorización -> Riesgo.
    """
    logs = []
    logs.append(f"[INFO] INICIO PROCESO: {objetivo.upper()}")
    
    # 1. Auditoría
    id_ejecucion = _crear_auditoria(objetivo, logs)
    if id_ejecucion == 0: 
        return "\n".join(logs)

    # 2. Búsqueda Web
    query_google = f"{objetivo} noticias denuncias colombia"
    urls = _buscar_en_google(query_google, logs)
    
    if not urls: 
        logs.append("[INFO] Sin resultados en búsqueda web.")
        return "\n".join(logs)

    stats = {"procesados": 0, "errores": 0, "vectores": 0}
    hallazgos_riesgo = []

    # 3. Procesamiento
    for i, url in enumerate(urls, 1):
        logs.append(f"\n[FUENTE {i}/{len(urls)}] {url}")
        
        try:
            # A. Scraping
            raw = scraper_engine.procesar(url)
            if not raw or raw.startswith("ERROR"):
                logs.append(f"   [SCRAPER FALLO] No se pudo obtener contenido.")
                stats["errores"] += 1
                continue
            
            titulo, texto = _parsear_contenido(raw)
            if len(texto) < 100:
                logs.append("   [INFO] Contenido insuficiente (<100 chars).")
                continue

            # B. Persistencia Documental
            id_doc = storage_engine.guardar_documento(id_ejecucion, titulo, url, texto)
            if not id_doc:
                logs.append("   [DB ERROR] Fallo al guardar documento maestro.")
                stats["errores"] += 1
                continue
            logs.append(f"   [DB] Documento guardado ID: {id_doc}")

            # C. Vectorización Global
            vector_doc = vectorizer_engine.generar_embedding(texto[:2000])
            if vector_doc is not None:
                storage_engine.guardar_vector_documento(id_doc, vector_doc)
                logs.append(f"   [IA] Embedding global guardado.")

            # D. Fragmentación y Análisis de Riesgo
            fragmentos = processor_engine.crear_fragmentos(texto)
            vectores_ok = 0
            
            for frag in fragmentos:
                txt = frag["texto"]
                seq = frag["nro_secuencia"]
                
                # Guardar fragmento
                id_frag = storage_engine.guardar_fragmento(id_doc, seq, txt)
                if not id_frag: continue
                
                # Vectorizar fragmento
                vector_frag = vectorizer_engine.generar_embedding(txt)
                
                if vector_frag is not None:
                    # Análisis de Riesgo
                    analisis = risk_engine.analizar_fragmento(txt)
                    
                    # Guardar análisis
                    storage_engine.guardar_analisis_vectorial(id_frag, vector_frag, analisis)
                    vectores_ok += 1
                    
                    if analisis["es_riesgo"]:
                        evidencia = (
                            f"[ALERTA] {analisis['etiqueta']}\n"
                            f"Contexto: \"{txt[:250]}...\"\n"
                            f"Origen: {url}"
                        )
                        hallazgos_riesgo.append(evidencia)
            
            stats["procesados"] += 1
            stats["vectores"] += vectores_ok

        except Exception as e:
            logs.append(f"   [EXCEPCION] Error no controlado: {str(e)}")
            stats["errores"] += 1

    # 4. Reporte Final
    reporte = [
        f"\nINFORME TÉCNICO: {objetivo.upper()}",
        f"="*50,
        f"Fuentes Procesadas: {stats['procesados']}",
        f"Errores Detectados: {stats['errores']}",
        f"Vectores Generados: {stats['vectores']}",
        f"="*50
    ]

    if hallazgos_riesgo:
        reporte.append("\nHALLAZGOS DE RIESGO:\n" + "\n\n".join(hallazgos_riesgo))
    else:
        reporte.append("\n[RESULTADO NEGATIVO] Sin indicadores de riesgo detectados.")

    reporte.append("\n--- LOG TÉCNICO ---\n" + "\n".join(logs))

    return "\n".join(reporte)