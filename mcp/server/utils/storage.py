import sys
import os
import json
import psycopg

# --- CONFIGURACION DE RUTAS E IMPORTACIONES ---
current_dir = os.path.dirname(os.path.abspath(__file__))
server_root = os.path.dirname(current_dir)

if server_root not in sys.path:
    sys.path.append(server_root)

# Importamos desde el nuevo core
from core.db.knowledge import get_connection

class Storage:
    """
    Capa de Persistencia (DAO) usando el nuevo core.
    """
    
    def _obtener_o_crear_etiqueta(self, cur, nombre_etiqueta: str) -> int:
        if not nombre_etiqueta or nombre_etiqueta == "NEUTRAL":
            return None
            
        try:
            sql_buscar = "SELECT id_etiquetariesgo FROM eco_aqua_etiquetariesgo WHERE nombre = %s"
            cur.execute(sql_buscar, (nombre_etiqueta,))
            resultado = cur.fetchone()
            
            if resultado:
                return resultado[0]
            
            sql_insertar = """
                INSERT INTO eco_aqua_etiquetariesgo (nombre, descripcion, nivel_prioridad)
                VALUES (%s, 'Generada automaticamente por el sistema IA', 1)
                RETURNING id_etiquetariesgo
            """
            cur.execute(sql_insertar, (nombre_etiqueta,))
            nuevo_id = cur.fetchone()[0]
            return nuevo_id
            
        except Exception as e:
            print(f"[DB WARNING] No se pudo resolver etiqueta '{nombre_etiqueta}': {e}", file=sys.stderr)
            return None

    def guardar_documento(self, id_exec: int, titulo: str, url: str, texto: str) -> int:
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
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
        finally:
            if conn: conn.close()

    def guardar_vector_documento(self, id_doc: int, vector: list):
        conn = None
        try:
            conn = get_connection()
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
        finally:
            if conn: conn.close()

    def guardar_fragmento(self, id_doc: int, secuencia: int, texto: str) -> int:
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
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
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()

    def guardar_analisis_vectorial(self, id_frag: int, vector: list, analisis: dict):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            confianza = analisis.get("confianza", 0.0)
            es_riesgo = analisis.get("es_riesgo", False)
            nombre_etiqueta = analisis.get("etiqueta", "NEUTRAL")
            
            id_etiqueta = self._obtener_o_crear_etiqueta(cur, nombre_etiqueta)
            
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
        finally:
            if conn: conn.close()

# Instancia global exportada
storage_engine = Storage()