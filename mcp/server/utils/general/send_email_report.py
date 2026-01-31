import os
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from utils.general.create_pdf import create_pdf as utils_create_pdf


def send_report_email(email: str, subject: str, message: str, content_pdf: str = None, name_pdf: str = "reporte.pdf") -> dict:
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
        # Validar credenciales
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        
        if not email_user or not email_password:
            return {
                "success": False,
                "error": "Credenciales de correo no configuradas. Verifique EMAIL_USER y EMAIL_PASSWORD en .env"
            }
        
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        if content_pdf:
            # Generar PDF usando Playwright
            pdf_result = utils_create_pdf(content_pdf, name_pdf)
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
        
        # Detectar servidor SMTP basado en el dominio del email
        if 'gmail' in email_user.lower():
            smtp_server = 'smtp.gmail.com'
        elif 'outlook' in email_user.lower() or 'hotmail' in email_user.lower():
            smtp_server = 'smtp.office365.com'
        else:
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        
        server = smtplib.SMTP(smtp_server, 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        
        return {"success": True}
        
    except smtplib.SMTPAuthenticationError as e:
        return {
            "success": False,
            "error": f"Error de autenticacion SMTP: {str(e)}. Verifique EMAIL_USER y EMAIL_PASSWORD."
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
