import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def run_diagnostic():
    print("🔍 INICIANDO DIAGNÓSTICO DE SISTEMA - AGENTE AQUA (MODO SEGURO)")
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
            print(f"✅ {label}: EXISTE")
        else:
            print(f"❌ {label}: NO ENCONTRADO")
            fs_ok = False
            
    if fs_ok:
        results.append("✅ Estructura de Recursos")
    else:
        results.append("❌ Estructura de Recursos (Incompleta)")

    # 2. VERIFICAR VARIABLES DE ENTORNO (.env)
    print("\n[2/5] Verificando Variables de Entorno...")
    env_path = server_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print("✅ Archivo .env: ENCONTRADO")
        
        # El usuario pidió GEMINI_API_KEY, pero en .env usamos GOOGLE_API_KEY (según config.py)
        # Verificamos ambos por si acaso o el que realmente se usa.
        needed_vars = ["DB_HOST", "DB_PORT", "GOOGLE_API_KEY", "GOOGLE_SEARCH_KEY"]
        missing_vars = []
        for var in needed_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if not missing_vars:
            print("✅ Variables críticas: CONFIGURADAS")
            results.append("✅ Variables de Entorno")
        else:
            print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
            results.append(f"❌ Variables de Entorno (Faltan: {len(missing_vars)})")
    else:
        print("❌ Archivo .env: NO ENCONTRADO")
        results.append("❌ Variables de Entorno (Sin .env)")

    # 3. VERIFICAR IMPORTS (Lógica)
    print("\n[3/5] Verificando Integridad de la Lógica (Imports)...")
    sys.path.insert(0, str(server_dir))
    
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
                print(f"✅ tools.aqua.{module_name}.{func_name}: OK")
            else:
                print(f"❌ tools.aqua.{module_name}: Función missing")
                logic_errors += 1
        except Exception as e:
            print(f"❌ tools.aqua.{module_name}: ERROR -> {e}")
            logic_errors += 1

    if logic_errors == 0:
        results.append("✅ Integridad de Lógica")
    else:
        results.append(f"❌ Integridad de Lógica ({logic_errors} errores)")

    # 4. PRUEBA DE CONEXIÓN A BD (No Bloqueante)
    print("\n[4/5] Probando Conexión a Base de Datos...")
    try:
        from utils.db import db_engine
        conn = db_engine.get_connection()
        if conn:
            print("✅ CONEXIÓN BD: EXITOSA")
            conn.close()
            results.append("✅ Conexión Base de Datos")
        else:
            print("🔴 BD Desconectada (Aviso): get_connection retornó None")
            results.append("⚠️ BD Desconectada (Aviso)")
    except Exception as e:
        print(f"🔴 BD Desconectada (Aviso): {e}")
        results.append("⚠️ BD Desconectada (Aviso)")

    # 5. RESUMEN FINAL
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL ESTADO DEL SISTEMA")
    print("=" * 60)
    for res in results:
        print(f" {res}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_diagnostic()
