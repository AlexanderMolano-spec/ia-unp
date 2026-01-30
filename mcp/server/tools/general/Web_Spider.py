"""
Tool: web_spider
Descripcion: Busqueda en prensa - visita URLs y busca palabras clave

NOTA: Este archivo es solo una referencia/documentacion.
La herramienta esta registrada en: servers/general.py
La implementacion esta en: utils/general/web_spider.py
"""

# Definicion de la herramienta (referencia)
# Nombre: web_spider
# Tags: ["GENERAL"]
#
# Argumentos:
#   - urls: list[str] - Lista de URLs iniciales a visitar
#   - keywords: list[str] - Lista de palabras clave para buscar
#       (ej: ["corrupcion", "gobierno", "investigacion"])
#   - deep_search: bool (opcional) - Si True, visita cada enlace encontrado (default: True)
#   - max_links_per_page: int (opcional) - Maximo de enlaces a analizar por pagina (None = sin limite)
#
# Retorna:
#   dict con:
#     - "success": bool
#     - "keywords_used": list - Palabras clave utilizadas
#     - "source_pages": dict - Informacion de las paginas fuente
#     - "analyzed_links": list - Lista de todos los enlaces analizados
#     - "matching_urls": list - Lista final de URLs con coincidencias
#     - "summary": dict - Resumen de resultados
