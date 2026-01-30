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
    """Capa de Persistencia (DAO) para el sistema Aqua.

    Maneja la insercion y consulta de documentos, fragmentos, vectores y resultados
    de analisis semanticos en la base de datos de conocimiento.
    """
    
    def _obtener_o_crear_etiqueta(self, cur, nombre_etiqueta: str) -> int:
        """Busca el ID de una etiqueta de riesgo o la crea si no existe.

        Args:
            cur: Cursor activo de psycopg.
            nombre_etiqueta: El nombre de la etiqueta a buscar/crear.

        Returns:
            int: El ID de la etiqueta de riesgo o None si falla.
        """
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
            # Salida de advertencia sobria
            print(f"WARNING: [DB] No se pudo resolver etiqueta '{nombre_etiqueta}': {e}", file=sys.stderr)
            return None

    def guardar_documento(self, id_exec: int, titulo: str, url: str, texto: str) -> int:
        """Guarda un documento maestro en la base de datos.

        Args:
            id_exec: ID de la ejecucion de la consulta asociada.
            titulo: Titulo extraido o asignado al documento.
            url: Origen del contenido.
            texto: Contenido textual completo.

        Returns:
            int: El ID del documento creado o 0 si ocurre un error.
        """
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return 0
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
            print(f"ERROR: [DB] Guardar Documento: {e}", file=sys.stderr)
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()

    def guardar_vector_documento(self, id_doc: int, vector: list):
        """Almacena el embedding global de un documento.

        Args:
            id_doc: ID del documento asociado.
            vector: Lista de floats que representan el embedding.
        """
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return
            cur = conn.cursor()
            sql = """
                INSERT INTO eco_aqua_documento_vector (id_documento, embedding)
                VALUES (%s, %s)
            """
            cur.execute(sql, (id_doc, str(vector)))
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"ERROR: [DB] Guardar Vector Doc: {e}", file=sys.stderr)
        finally:
            if conn: conn.close()

    def guardar_fragmento(self, id_doc: int, secuencia: int, texto: str) -> int:
        """Guarda un fragmento individual perteneciente a un documento.

        Args:
            id_doc: ID del documento padre.
            secuencia: Numero de orden del fragmento.
            texto: Contenido textual del fragmento.

        Returns:
            int: El ID del fragmento creado o 0 si ocurre un error.
        """
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return 0
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
            print(f"ERROR: [DB] Guardar Fragmento: {e}", file=sys.stderr)
            if conn: conn.rollback()
            return 0
        finally:
            if conn: conn.close()

    def guardar_analisis_vectorial(self, id_frag: int, vector: list, analisis: dict):
        """Guarda el embedding de un fragmento y el resultado de su analisis de riesgo.

        Args:
            id_frag: ID del fragmento asociado.
            vector: Embedding del fragmento.
            analisis: Diccionario con los hallazgos del RiskEngine.
        """
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return
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
            print(f"ERROR: [DB] Guardar Analisis Vectorial: {e}", file=sys.stderr)
        finally:
            if conn: conn.close()

# Instancia global exportada para uso concurrente
storage_engine = Storage()