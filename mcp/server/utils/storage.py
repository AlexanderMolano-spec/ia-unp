import sys
import os
import json

# --- CONFIGURACION DE RUTAS E IMPORTACIONES ---
# Obtiene la ruta absoluta del directorio actual ('tools')
current_dir = os.path.dirname(os.path.abspath(__file__))
# Obtiene el directorio padre ('Aqua') para permitir importaciones relativas
aqua_root = os.path.dirname(current_dir)

# Agrega la raiz del servidor Aqua al path del sistema si no existe
if aqua_root not in sys.path:
    sys.path.append(aqua_root)

try:
    # Intenta importar el gestor de base de datos desde el nucleo local
    from utils.db import db_engine
except ImportError:
    from db import db_engine

class Storage:
    """
    Capa de Persistencia (DAO).
    Maneja el guardado en PostgreSQL alineado con estructura.sql.
    Incluye logica para resolver relaciones de claves foraneas (etiquetas).
    """
    
    def _obtener_o_crear_etiqueta(self, cur, nombre_etiqueta: str) -> int:
        """
        Metodo privado auxiliar.
        Busca el ID de una etiqueta por su nombre. Si no existe, la crea.
        
        Args:
            cur: Cursor de base de datos activo.
            nombre_etiqueta (str): El nombre de la etiqueta (ej: 'Amenaza').
            
        Returns:
            int: El ID (id_etiquetariesgo) correspondiente. Retorna None si falla.
        """
        if not nombre_etiqueta or nombre_etiqueta == "NEUTRAL":
            return None
            
        try:
            # 1. Intentar buscar la etiqueta existente
            sql_buscar = "SELECT id_etiquetariesgo FROM eco_aqua_etiquetariesgo WHERE nombre = %s"
            cur.execute(sql_buscar, (nombre_etiqueta,))
            resultado = cur.fetchone()
            
            if resultado:
                return resultado[0]
            
            # 2. Si no existe, crearla dinamicamente
            # Se asume nivel_prioridad 0 por defecto segun el DDL
            sql_insertar = """
                INSERT INTO eco_aqua_etiquetariesgo (nombre, descripcion, nivel_prioridad)
                VALUES (%s, 'Generada automaticamente por el sistema IA', 1)
                RETURNING id_etiquetariesgo
            """
            cur.execute(sql_insertar, (nombre_etiqueta,))
            nuevo_id = cur.fetchone()[0]
            return nuevo_id
            
        except Exception as e:
            # Si falla (ej: condicion de carrera), retornamos None para no romper el flujo principal
            print(f"[DB WARNING] No se pudo resolver etiqueta '{nombre_etiqueta}': {e}", file=sys.stderr)
            return None

    def guardar_documento(self, id_exec: int, titulo: str, url: str, texto: str) -> int:
        """
        Guarda el documento maestro.
        """
        if db_engine is None: return 0
        conn = db_engine.get_connection()
        if not conn: return 0
        
        try:
            cur = conn.cursor()
            # Mapeo exacto segun estructura.sql
            sql = """
                INSERT INTO eco_aqua_documento 
                (id_ejecucionconsulta, titulo, url, texto_completo, fecha_registro)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING id_documento
            """
            cur.execute(sql, (id_exec, titulo, url, texto))
            id_doc = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return id_doc
        except Exception as e:
            print(f"[DB ERROR] Guardar Documento: {e}", file=sys.stderr)
            if conn: conn.rollback()
            return 0

    def guardar_vector_documento(self, id_doc: int, vector: list):
        """
        Guarda el embedding global del documento.
        """
        if db_engine is None: return
        conn = db_engine.get_connection()
        if not conn: return
        
        try:
            cur = conn.cursor()
            sql = """
                INSERT INTO eco_aqua_documento_vector (id_documento, embedding)
                VALUES (%s, %s)
            """
            cur.execute(sql, (id_doc, str(vector)))
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"[DB ERROR] Guardar Vector Doc: {e}", file=sys.stderr)

    def guardar_fragmento(self, id_doc: int, secuencia: int, texto: str) -> int:
        """
        Guarda el fragmento de texto.
        """
        if db_engine is None: return 0
        conn = db_engine.get_connection()
        if not conn: return 0
        
        try:
            cur = conn.cursor()
            # Mapeo: texto -> texto_fragmento (segun estructura.sql)
            sql = """
                INSERT INTO eco_aqua_fragmento (id_documento, nro_secuencia, texto_fragmento)
                VALUES (%s, %s, %s)
                RETURNING id_fragmento
            """
            cur.execute(sql, (id_doc, secuencia, texto))
            id_frag = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return id_frag
        except Exception as e:
            print(f"[DB ERROR] Guardar Fragmento: {e}", file=sys.stderr)
            return 0

    def guardar_analisis_vectorial(self, id_frag: int, vector: list, analisis: dict):
        """
        Guarda el vector, analisis de riesgo y ENLAZA la etiqueta de riesgo (FK).
        """
        if db_engine is None: return
        conn = db_engine.get_connection()
        if not conn: return
        
        try:
            cur = conn.cursor()
            
            # 1. Obtener datos del analisis
            confianza = analisis.get("confianza", 0.0)
            es_riesgo = analisis.get("es_riesgo", False)
            nombre_etiqueta = analisis.get("etiqueta", "NEUTRAL")
            
            # 2. Resolver el ID de la etiqueta (Foreign Key)
            # Esto busca el ID correspondiente al texto (ej: "Amenaza" -> ID 5)
            id_etiqueta = self._obtener_o_crear_etiqueta(cur, nombre_etiqueta)
            
            # 3. Insertar en la tabla fragmento_vector
            # Mapeo de columnas segun estructura.sql:
            # - vector_embedding -> embedding
            # - fatalidad_detectada -> es_riesgo
            # - id_etiquetariesgo -> id_etiqueta (Entero resuelto)
            
            sql = """
                INSERT INTO eco_aqua_fragmento_vector 
                (id_fragmento, embedding, confianza, fatalidad_detectada, fecha_analisis, id_etiquetariesgo)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """
            cur.execute(sql, (
                id_frag, 
                str(vector), 
                confianza,
                es_riesgo,
                id_etiqueta
            ))
            conn.commit()
            cur.close()
            
        except Exception as e:
            print(f"[DB ERROR] Guardar Analisis Vectorial: {e}", file=sys.stderr)

# Instancia global exportada
storage_engine = Storage()