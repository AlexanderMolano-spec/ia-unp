import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def run_diagnostic():
    """Ejecuta un diagnostico integral del sistema Aqua.

    Verifica la estructura de archivos, la configuracion del entorno (.env),
    la integridad de los imports y la conectividad con servicios externos.
    """
    print("INFO: [DIAGNOSTICO] INICIO DE VERIFICACION DE SISTEMA - AGENTE AQUA")
    print("=" * 60)
    
    results = []
    
    # 1. VERIFICAR ESTRUCTURA DE CARPETAS Y RECURSOS
    print("\n[1/5] Verificando Estructura de Carpetas y Recursos...")
    server_dir = Path(__file__).parent
    
    checks_fs = [
        ("resources/data_dictionary.md", server_dir / "resources" / "data_dictionary.md"),
        ("prompts/prompt_reporte_objetivo.md", server_dir / "prompts" / "prompt_reporte_objetivo.md"),
        ("prompts/prompt_evaluacion_forense.md", server_dir / "prompts" / "prompt_evaluacion_forense.md")
    ]
    
    fs_ok = True
    for label, path in checks_fs:
        if path.exists():
            print(f"SUCCESS: {label} encontrado.")
        else:
            print(f"ERROR: {label} no encontrado.")
            fs_ok = False
            
    if fs_ok:
        results.append("SUCCESS: Estructura de Recursos")
    else:
        results.append("ERROR: Estructura de Recursos (Incompleta)")

    # 2. VERIFICAR VARIABLES DE ENTORNO (.env)
    print("\n[2/5] Verificando Variables de Entorno...")
    env_path = server_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print("SUCCESS: Archivo .env cargado.")
        
        needed_vars = [
            "KNOWLEDGE_DB_HOST", "KNOWLEDGE_DB_PORT", "KNOWLEDGE_DB_NAME", 
            "KNOWLEDGE_DB_USER", "KNOWLEDGE_DB_PASSWORD",
            "GOOGLE_API_KEY", "GOOGLE_SEARCH_KEY", "GOOGLE_CX_ID",
            "SCRAPER_SERVICE_ENABLED", "SCRAPER_SERVICE_BASE_URL", "SCRAPER_SERVICE_TIMEOUT"
        ]
        missing_vars = []
        for var in needed_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if not missing_vars:
            print("SUCCESS: Todas las variables criticas estan configuradas.")
            results.append("SUCCESS: Variables de Entorno")
        else:
            print(f"ERROR: Variables faltantes: {', '.join(missing_vars)}")
            results.append(f"ERROR: Variables de Entorno (Faltan: {len(missing_vars)})")
    else:
        print("ERROR: Archivo .env no encontrado.")
        results.append("ERROR: Variables de Entorno (Sin .env)")

    # 3. VERIFICAR IMPORTS (Logica Core)
    print("\n[3/5] Verificando Integridad de la Logica (Core & Tools)...")
    sys.path.insert(0, str(server_dir))
    
    try:
        from core.config import get_settings
        from core.db.knowledge import get_connection
        print("SUCCESS: core.config: OK")
        print("SUCCESS: core.db.knowledge: OK")
    except Exception as e:
        print(f"ERROR: Fallo en Core: {e}")

    logic_checks = [
        ("investigar_objetivo", "logic_investigar_objetivo"),
        ("consultar_rag", "logic_consultar_rag"),
        ("consultar_conocimiento", "logic_consultar_conocimiento"),
        ("reportar_objetivo", "logic_reportar_objetivo"),
        ("evaluar_hechos", "logic_evaluar_hechos")
    ]
    
    logic_errors = 0
    for module_name, func_name in logic_checks:
        try:
            module = __import__(f"tools.aqua.{module_name}", fromlist=[func_name])
            if hasattr(module, func_name):
                print(f"SUCCESS: tools.aqua.{module_name}.{func_name}: OK")
            else:
                print(f"ERROR: tools.aqua.{module_name}: Funcion faltante")
                logic_errors += 1
        except Exception as e:
            print(f"ERROR: tools.aqua.{module_name}: {e}")
            logic_errors += 1

    if logic_errors == 0:
        results.append("SUCCESS: Integridad de Logica")
    else:
        results.append(f"ERROR: Integridad de Logica ({logic_errors} errores)")

    # 4. PRUEBA DE CONEXION A SERVICIOS (DB & Scraper)
    print("\n[4/5] Probando Conexion a Servicios...")
    
    # A. Base de Datos
    try:
        from core.db.knowledge import get_connection
        conn = get_connection()
        if conn:
            print("SUCCESS: CONEXION BD: ESTABLECIDA")
            conn.close()
            results.append("SUCCESS: Conexion Base de Datos")
        else:
            print("WARNING: BD Desconectada (Aviso): get_connection retorno None")
            results.append("WARNING: BD Desconectada (Aviso)")
    except Exception as e:
        print(f"WARNING: BD Desconectada (Aviso): {e}")
        results.append("WARNING: BD Desconectada (Aviso)")

    # B. Scraper Service (Health Check)
    import requests
    scraper_enabled = os.getenv("SCRAPER_SERVICE_ENABLED", "false").lower() == "true"
    scraper_base_url = os.getenv("SCRAPER_SERVICE_BASE_URL")
    
    if scraper_enabled and scraper_base_url:
        print(f"INFO: [NETWORK] Verificando Scraper en: {scraper_base_url}")
        try:
            resp = requests.get(scraper_base_url, timeout=5)
            if resp.status_code < 500:
                print(f"SUCCESS: [NETWORK] SERVICIO SCRAPER: DISPONIBLE (Status: {resp.status_code})")
                results.append("SUCCESS: Conexion Scraper Service")
            else:
                print(f"ERROR: [NETWORK] SERVICIO SCRAPER: ERROR HTTP {resp.status_code}")
                results.append("ERROR: Conexion Scraper Service (Error HTTP)")
        except Exception as e:
            print(f"ERROR: [NETWORK] SERVICIO SCRAPER: NO DISPONIBLE -> {e}")
            results.append("ERROR: Conexion Scraper Service (Offline)")
    elif not scraper_enabled:
        print("INFO: SERVICIO SCRAPER: DESHABILITADO en .env")
        results.append("INFO: Scraper Service Deshabilitado")
    else:
        results.append("WARNING: Scraper Service Base URL no configurada")

    # 5. RESUMEN FINAL
    print("\n" + "=" * 60)
    print("RESUMEN DEL ESTADO DEL SISTEMA")
    print("=" * 60)
    for res in results:
        print(f" {res}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_diagnostic()
