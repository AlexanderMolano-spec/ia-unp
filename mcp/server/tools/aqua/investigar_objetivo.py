import sys
import requests
from typing import List, Tuple, Optional
from urllib.parse import urljoin

# Importamos desde core y utils
from core.config import get_settings
from utils.config import get_app_settings
from core.db.knowledge import get_connection

# Motores (Servicios de Aqua en utils)
from utils.text_processor import processor_engine
from utils.vectorizer import vectorizer_engine
from utils.risk_engine import risk_engine
from utils.storage import storage_engine

# --- FUNCIONES PRIVADAS (Helpers) ---

def _buscar_en_google(query: str, logs: List[str]) -> List[str]:
    """Ejecuta búsqueda en Google Custom Search API.

    Args:
        query: La cadena de busqueda para Google.
        logs: Lista de logs acumulados para registrar eventos.

    Returns:
        Lista de URLs encontradas.
    """
    app_settings = get_app_settings()
    if not app_settings.google_search_key or not app_settings.google_cx_id:
        logs.append("ERROR CONFIG: Credenciales de Google Search no configuradas.")
        return []
    
    logs.append(f"INFO: [SEARCH] Consulta: '{query}'")
    urls = []
    try:
        url_api = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": app_settings.google_search_key, 
            "cx": app_settings.google_cx_id, 
            "q": query, 
            "num": 5,
            "gl": "co"
        }
        resp = requests.get(url_api, params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "items" in data:
                urls = [item["link"] for item in data["items"]]
                logs.append(f"INFO: [SEARCH] Exito: {len(urls)} resultados.")
        else:
            logs.append(f"ERROR: [SEARCH] Codigo API: {resp.status_code}")
            
    except Exception as e:
        logs.append(f"ERROR: [SEARCH] Excepcion: {str(e)}")
    return urls

def _crear_auditoria(target: str, logs: List[str]) -> int:
    """Registra el inicio de una investigacion en la base de datos.

    Args:
        target: El objetivo de la investigacion.
        logs: Lista de logs para auditoria textual.

    Returns:
        ID de la ejecucion creada o 0 si fallo.
    """
    conn = None
    try:
        conn = get_connection()
        if not conn:
            logs.append("ERROR DB: No se pudo conectar para registrar auditoria.")
            return 0
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
        logs.append(f"INFO: [AUDIT] Registro creado ID: {id_exec}")
        return id_exec
    except Exception as e:
        logs.append(f"ERROR: [AUDIT] {e}")
        return 0
    finally:
        if conn:
            conn.close()

def _llamar_servicio_scraper(urls: List[str], logs: List[str]) -> List[dict]:
    """Realiza la llamada al microservicio de Scraping (Docker).

    Args:
        urls: Lista de URLs a procesar.
        logs: Lista de logs para seguimiento.

    Returns:
        Lista de diccionarios con los resultados del scraping (titulo, texto, url, error).
    """
    app_settings = get_app_settings()
    
    if not app_settings.scraper_service_enabled:
        logs.append("INFO: El servicio de Scraping esta deshabilitado en la configuracion.")
        return []

    if not app_settings.scraper_service_base_url:
        logs.append("ERROR CONFIG: SCRAPER_SERVICE_BASE_URL no configurada.")
        return []
    
    # Construcción dinámica de la URL
    endpoint = urljoin(app_settings.scraper_service_base_url, "/extract")
    logs.append(f"INFO: [NETWORK] Delegando {len(urls)} URLs al servicio en {endpoint}...")
    
    try:
        payload = {
            "urls": urls,
            "lang": "es",
            "concurrency": 6
        }
        
        # Uso del timeout configurado
        timeout = app_settings.scraper_service_timeout
        resp = requests.post(endpoint, json=payload, timeout=timeout)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                resultados = data.get("results", [])
                logs.append(f"SUCCESS: [NETWORK] Servicio respondio con {len(resultados)} resultados.")
                return resultados
        
        logs.append(f"ERROR: [NETWORK] Servicio retorno status {resp.status_code}")
        return []
        
    except requests.exceptions.ConnectionError:
        logs.append(f"WARNING: [NETWORK] Error de conexion con el servicio de Scraping en {endpoint} (¿Estado del contenedor?)")
        return []
    except requests.exceptions.Timeout:
        logs.append(f"WARNING: [NETWORK] Tiempo de espera agotado ({timeout}s) conectando a {endpoint}")
        return []
    except Exception as e:
        logs.append(f"ERROR: [NETWORK] Excepcion: {str(e)}")
        return []

# --- LÓGICA PRINCIPAL ---

def logic_investigar_objetivo(objetivo: str) -> str:
    """Orquesta el proceso completo de investigacion de un objetivo.

    Flujo: Búsqueda -> Scraping (Docker) -> Persistencia -> Vectorización -> Análisis de Riesgo.

    Args:
        objetivo: Nombre de la persona o entidad a investigar.

    Returns:
        Un informe técnico detallado con hallazgos de riesgo y logs de ejecucion.
    """
    logs = []
    logs.append(f"INFO: INICIO PROCESO: {objetivo.upper()}")
    
    # 1. Auditoría
    id_ejecucion = _crear_auditoria(objetivo, logs)
    if id_ejecucion == 0: 
        return "\n".join(logs)

    # 2. Búsqueda Web
    query_google = f"{objetivo} noticias denuncias colombia"
    urls = _buscar_en_google(query_google, logs)
    
    if not urls: 
        logs.append("INFO: Sin resultados en busqueda web.")
        return "\n".join(logs)

    # 3. Llamada masiva al Scraper Service
    resultados_scraper = _llamar_servicio_scraper(urls, logs)
    
    if not resultados_scraper:
        logs.append("INFO: No se obtuvo contenido del servicio de Scraping.")
        return "\n".join(logs)

    stats = {"procesados": 0, "errores": 0, "vectores": 0}
    hallazgos_riesgo = []

    # 4. Procesamiento de Resultados
    for res in resultados_scraper:
        url = res.get("url")
        titulo = res.get("titulo", "Sin Título")
        texto = res.get("texto", "")
        error = res.get("error")
        
        logs.append(f"\nINFO: [MARK] ANALIZANDO: {url}")
        
        if error:
            logs.append(f"   ERROR: [NETWORK] Fallo en fuente: {error}")
            stats["errores"] += 1
            continue
            
        if not texto or len(texto) < 100:
            logs.append("   INFO: Contenido insuficiente o vacio.")
            continue

        try:
            # B. Persistencia Documental
            id_doc = storage_engine.guardar_documento(id_ejecucion, titulo, url, texto)
            if not id_doc:
                logs.append("   ERROR DB: Fallo al guardar documento maestro.")
                stats["errores"] += 1
                continue
            logs.append(f"   INFO: [FILE] Documento guardado ID: {id_doc}")

            # C. Vectorización Global
            vector_doc = vectorizer_engine.generar_embedding(texto[:2000])
            if vector_doc is not None:
                storage_engine.guardar_vector_documento(id_doc, vector_doc)
                logs.append(f"   INFO: [IA] Embedding global guardado.")

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
                            f"WARNING: [ALERTA] {analisis['etiqueta']}\n"
                            f"Contexto: \"{txt[:250]}...\"\n"
                            f"Origen: {url}"
                        )
                        hallazgos_riesgo.append(evidencia)
            
            stats["procesados"] += 1
            stats["vectores"] += vectores_ok

        except Exception as e:
            logs.append(f"   ERROR SISTEMA: Error no controlado: {str(e)}")
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
        reporte.append("\nINFO: [RESULTADO NEGATIVO] Sin indicadores de riesgo detectados.")

    reporte.append("\n--- LOG TÉCNICO ---\n" + "\n".join(logs))

    return "\n".join(reporte)