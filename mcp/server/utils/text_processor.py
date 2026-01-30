import spacy
import sys
from typing import List, Dict, Any

# CARGA SILENCIOSA: Sin prints, sin avisos para no ensuciar logs.
nlp = None
try:
    # Intenta cargar modelo grande (recomendado para produccion)
    nlp = spacy.load("es_core_news_lg")
except OSError:
    try:
        # Fallback a modelo pequeño (desarrollo/local)
        nlp = spacy.load("es_core_news_sm")
    except OSError:
        # Fallback total: No hay spacy instalado
        nlp = None

class TextProcessor:
    """
    Procesador de Texto Inteligente.
    Divide textos largos en fragmentos semanticos utilizando NLP si esta disponible,
    o particion por caracteres si no hay modelos instalados.
    """
    
    def crear_fragmentos(self, texto_completo: str, tamano_ventana: int = 3) -> List[Dict[str, Any]]:
        """
        Genera fragmentos solapados o secuenciales del texto.
        
        Args:
            texto_completo (str): Texto a procesar.
            tamano_ventana (int): Numero de oraciones por fragmento (si usa Spacy).
        """
        if not texto_completo or len(texto_completo.strip()) == 0:
            return []

        # Limpieza basica de lineas vacias
        lineas_sucias = texto_completo.split('\n')
        lineas_limpias = [l.strip() for l in lineas_sucias if len(l.strip()) > 50]
        texto_limpio = " ".join(lineas_limpias)
        
        if len(texto_limpio) < 50: return []

        fragmentos = []
        usar_fallback = False

        if nlp:
            try:
                # Aumentar limite para textos muy grandes
                nlp.max_length = 4000000 
                doc = nlp(texto_limpio)
                
                # Filtrar oraciones muy cortas que suelen ser ruido
                oraciones = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
                
                if oraciones:
                    secuencia = 1
                    total = len(oraciones)
                    if total <= tamano_ventana:
                        fragmentos.append({"nro_secuencia": 1, "texto": texto_limpio})
                    else:
                        # Ventana deslizante de oraciones
                        for i in range(0, total, tamano_ventana):
                            chunk = " ".join(oraciones[i : i + tamano_ventana])
                            if len(chunk) > 30:
                                fragmentos.append({"nro_secuencia": secuencia, "texto": chunk})
                                secuencia += 1
                else:
                    usar_fallback = True
            except:
                usar_fallback = True
        else:
            usar_fallback = True

        # Metodo Fallback: Particion por longitud fija de caracteres
        if usar_fallback or not fragmentos:
            tamano_bloque = 1000
            secuencia = 1
            for i in range(0, len(texto_limpio), tamano_bloque):
                chunk = texto_limpio[i : min(i + tamano_bloque, len(texto_limpio))]
                fragmentos.append({"nro_secuencia": secuencia, "texto": chunk})
                secuencia += 1

        return fragmentos

# Instancia global exportada
processor_engine = TextProcessor()