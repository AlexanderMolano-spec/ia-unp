"""
Tool: send_email_report
Descripcion: Envio de correo electronico con opcion de adjuntar PDF

Registro MCP: main.py

Variables de entorno requeridas:
    SMTP_HOST: Servidor SMTP (ej: smtp.gmail.com)
    SMTP_PORT: Puerto SMTP (default: 587)
    SMTP_USER: Usuario/correo para autenticacion
    SMTP_PASSWORD: Contraseña o App Password
    SMTP_FROM: Direccion de remitente (opcional, usa SMTP_USER si no se especifica)
    SMTP_USE_TLS: Usar TLS (default: true)
"""

import os
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from tools.general.create_pdf import logic_create_pdf


async def logic_send_email_report(
    email: str,
    subject: str,
    message: str,
    content_pdf: str = None,
    name_pdf: str = "reporte.pdf"
) -> dict:
    """
    Envia un correo electronico con opcion de adjuntar un PDF generado desde HTML.
    
    Args:
        email: Direccion de correo del destinatario
        subject: Asunto del correo
        message: Cuerpo del mensaje en texto plano
        content_pdf: Contenido HTML para generar el PDF (opcional)
        name_pdf: Nombre del archivo PDF adjunto (opcional, default: "reporte.pdf")
    
    Returns:
        dict: Diccionario con:
            - "success": bool - True si el correo se envio correctamente
            - "error": str - Mensaje de error (si success=False)
    """
    try:
        # Cargar configuracion SMTP desde variables de entorno
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_from = os.getenv("SMTP_FROM", smtp_user)  # Usa SMTP_USER si no hay SMTP_FROM
        smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
        
        # Validar configuracion requerida
        if not smtp_host:
            return {
                "success": False,
                "error": "SMTP_HOST no configurado en .env"
            }
        
        if not smtp_user or not smtp_password:
            return {
                "success": False,
                "error": "Credenciales SMTP no configuradas. Verifique SMTP_USER y SMTP_PASSWORD en .env"
            }
        
        # Construir el mensaje
        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # Adjuntar PDF si se proporciona contenido HTML
        if content_pdf:
            pdf_result = await logic_create_pdf(content_pdf, name_pdf)
            if pdf_result["success"]:
                pdf_bytes = base64.b64decode(pdf_result["pdf_base64"])
                part = MIMEApplication(pdf_bytes, Name=name_pdf)
                part['Content-Disposition'] = f'attachment; filename="{name_pdf}"'
                msg.attach(part)
            else:
                return {
                    "success": False,
                    "error": f"Error al generar PDF adjunto: {pdf_result.get('error', 'Error desconocido')}"
                }
        
        # Conectar al servidor SMTP y enviar
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.ehlo()
        
        if smtp_use_tls:
            server.starttls()
            server.ehlo()
        
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return {"success": True}
        
    except smtplib.SMTPAuthenticationError as e:
        return {
            "success": False,
            "error": f"Error de autenticacion SMTP: {str(e)}. Verifique SMTP_USER y SMTP_PASSWORD."
        }
    except smtplib.SMTPConnectError as e:
        return {
            "success": False,
            "error": f"Error de conexion al servidor SMTP: {str(e)}"
        }
    except smtplib.SMTPRecipientsRefused as e:
        return {
            "success": False,
            "error": f"Destinatario rechazado: {str(e)}"
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "error": f"Error SMTP: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error inesperado al enviar correo: {type(e).__name__}: {str(e)}"
        }
