import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Configurar el path para importaciones locales
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Cargar variables de entorno
load_dotenv(BASE_DIR / ".env")

try:
    from tools.aqua.investigar_objetivo import logic_investigar_objetivo
except ImportError as e:
    print(f"❌ Error al importar la herramienta: {e}")
    sys.exit(1)

async def main():
    print("\n" + "="*60)
    print("🕵️  SISTEMA DE INVESTIGACIÓN DE PERSONAS - EI-UNP")
    print("="*60)
    
    try:
        # Pedir entrada al usuario
        nombre_persona = input("\n👤 Ingresa el nombre de la persona a investigar: ").strip()
        
        if not nombre_persona:
            print("⚠️ El nombre no puede estar vacío.")
            return

        print(f"\n🔍 Iniciando investigación de: {nombre_persona.upper()}...")
        print("⏳ Este proceso puede tardar unos minutos (Búsqueda, Scraping, IA)...")
        
        # Ejecutar la lógica de investigación
        # Nota: La función actual es síncrona según el código visto, 
        # pero la envolvemos por si hay cambios futuros a async.
        loop = asyncio.get_event_loop()
        resultado = await loop.run_in_executor(None, logic_investigar_objetivo, nombre_persona)
        
        print("\n" + "🏁" + " RESULTADO DE LA INVESTIGACIÓN ".center(56, "=") + "🏁")
        print(resultado)
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Investigación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA INVESTIGACIÓN: {str(e)}")
    finally:
        print("\n📊 Fin de la operación.\n")

if __name__ == "__main__":
    asyncio.run(main())
