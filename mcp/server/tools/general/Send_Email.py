"""
Tool: send_email_report
Descripcion: Envio de correo electronico con opcion de adjuntar PDF

NOTA: Este archivo es solo una referencia/documentacion.
La herramienta esta registrada en: servers/general.py
La implementacion esta en: utils/general/send_email_report.py
"""

# Definicion de la herramienta (referencia)
# Nombre: send_email_report
# Tags: ["GENERAL"]
#
# Argumentos:
#   - email: str - Direccion de correo del destinatario
#   - subject: str - Asunto del correo
#   - message: str - Cuerpo del mensaje en texto plano
#   - content_pdf: str (opcional) - Contenido HTML para generar el PDF adjunto
#   - name_pdf: str (opcional) - Nombre del archivo PDF (default: "reporte.pdf")
#
# Retorna:
#   dict con:
#     - "success": bool - True si el correo se envio correctamente
#     - "error": str - Mensaje de error (si success=False)