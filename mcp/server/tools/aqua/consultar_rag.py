from typing import List
from core.db.knowledge import get_connection
from utils.vectorizer import vectorizer_engine

def logic_consultar_rag(consulta: str) -> str:
    """Busca antecedentes internos utilizando Retrieval-Augmented Generation (RAG).

    Vectoriza la consulta del usuario y realiza una busqueda de similitud semantica
    en la base de datos de documentos procesados de la UNP.

    Args:
        consulta: El termino o pregunta de busqueda semantica.

    Returns:
        Una cadena formateada con los documentos mas relevantes encontrados,
        incluyendo titulo, extracto y porcentaje de similitud.

    Raises:
        Exception: Si ocurre un error en la vectorizacion o la consulta a la base de datos.
    """
    try:
        # 1. Generar Vector
        vector = vectorizer_engine.generar_embedding(consulta)
        
        if vector is None:
            return "ERROR: El motor de vectorizacion fallo."

        # 2. Conexion a BD
        conn = None
        try:
            conn = get_connection()
            if not conn:
                return "ERROR DB: No se pudo conectar a la base de datos de conocimiento."
                
            cur = conn.cursor()
            
            # 3. Consulta SQL (RAG)
            sql = """
                SELECT d.titulo, d.texto_completo, (v.embedding <=> %s::vector) as distancia
                FROM eco_aqua_documento d
                JOIN eco_aqua_documento_vector v ON d.id_documento = v.id_documento
                ORDER BY distancia ASC
                LIMIT 3;
            """
            
            cur.execute(sql, (str(vector),))
            resultados = cur.fetchall()
            cur.close()
        finally:
            if conn:
                conn.close()
        
        if not resultados: 
            return "INFO: [MEMORIA] No se encontraron antecedentes previos relacionados."
        
        # 4. Formatear
        res = [f"--- ANTECEDENTES INTERNOS: '{consulta}' ---"]
        
        for titulo, texto, distancia in resultados:
            similitud = (1 - distancia) * 100
            res.append(f"\nINFO: [FILE] TITULO: {titulo}")
            res.append(f"   Similitud: {similitud:.1f}%")
            res.append(f"   Extracto: \"{texto[:500]}...\"")
            
        return "\n".join(res)
        
    except Exception as e:
        return f"ERROR SISTEMA: {str(e)}"
