from typing import List
from utils.db import db_engine
# Importamos el ENGINE correctamente
from utils.vectorizer import vectorizer_engine

def logic_consultar_rag(consulta: str) -> str:
    """
    Lógica interna: Vectoriza la consulta y busca similitudes en la BD (RAG).
    """
    try:
        # 1. Generar Vector
        vector = vectorizer_engine.generar_embedding(consulta)
        
        if vector is None:
            return "[ERROR] El motor de vectorización falló."

        # 2. Conexión a BD
        conn = db_engine.get_connection()
        if not conn:
            return "[ERROR] No hay conexión activa con la base de datos."

        cur = conn.cursor()
        
        # 3. Consulta SQL (RAG)
        sql = """
            SELECT d.titulo, d.texto_completo, (v.embedding <=> %s::vector) as distancia
            FROM eco_aqua_documento d
            JOIN eco_aqua_documento_vector v ON d.id_documento = v.id_documento
            ORDER BY distancia ASC
            LIMIT 3;
        """
        
        cur.execute(sql, (str(vector.tolist()),))
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        
        if not resultados: 
            return "[MEMORIA] No se encontraron antecedentes previos."
        
        # 4. Formatear
        res = [f"--- ANTECEDENTES INTERNOS: '{consulta}' ---"]
        
        for titulo, texto, distancia in resultados:
            similitud = (1 - distancia) * 100
            res.append(f"\n📂 TÍTULO: {titulo}")
            res.append(f"   Similitud: {similitud:.1f}%")
            res.append(f"   Extracto: \"{texto[:500]}...\"")
            
        return "\n".join(res)
        
    except Exception as e:
        return f"[ERROR SISTEMA] {str(e)}"
