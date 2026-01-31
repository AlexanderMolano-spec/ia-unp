"""
Tool: create_pdf
Descripcion: Creacion de PDF a partir de HTML

NOTA: Este archivo es solo una referencia/documentacion.
La herramienta esta registrada en: servers/general.py
La implementacion esta en: utils/general/create_pdf.py
"""

# Definicion de la herramienta (referencia)
# Nombre: create_pdf
# Tags: ["GENERAL"]
#
# Argumentos:
#   - html: str - HTML a convertir a PDF
#   - filename: str (opcional) - Nombre del archivo PDF (default: "reporte.pdf")
#
# Retorna:
#   dict con:
#     - "success": bool - True si se creo correctamente
#     - "pdf_base64": str - Contenido del PDF codificado en base64 (si success=True)
#     - "filename": str - Nombre del archivo PDF
#     - "mime_type": str - Tipo MIME del archivo ("application/pdf")
#     - "error": str - Mensaje de error (si success=False)
#
# Ejemplo de uso desde cliente MCP:
#   El cliente recibira un dict con pdf_base64 que puede decodificar y guardar.
