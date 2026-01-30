import sys
import os
import psycopg2

# --- AJUSTE DINAMICO DE IMPORTACIONES ---
# Asegura que se pueda importar Config desde el directorio local
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from utils.config import Config
except ImportError:
    from config import Config

class DatabaseHandler:
    """
    Gestor Central de Conexiones a PostgreSQL.
    Patron Singleton para eficiencia de recursos.
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHandler, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def get_connection(self):
        """
        Retorna una nueva conexion a la base de datos.
        """
        try:
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                port=Config.DB_PORT
            )
            return conn
        except Exception as e:
            print(f"[ERROR CRITICO DB] No se pudo conectar a PostgreSQL: {e}", file=sys.stderr)
            return None

    def return_connection(self, conn):
        """
        Cierra la conexion de manera segura.
        """
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[ERROR DB] Error cerrando conexion: {e}", file=sys.stderr)

# Instancia global exportada
db_engine = DatabaseHandler()