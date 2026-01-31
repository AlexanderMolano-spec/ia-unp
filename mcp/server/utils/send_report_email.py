import os
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def _guess_smtp_server(email_user: str) -> str:
    domain = email_user.split("@")[-1].lower().strip()

    if domain in {"gmail.com", "googlemail.com"}:
        return "smtp.gmail.com"
    if domain in {"outlook.com", "hotmail.com", "live.com"}:
        return "smtp.office365.com"

    # Fallback explícito por env
    return os.getenv("SMTP_SERVER", "smtp.gmail.com")


def send_report_email(
    email: str,
    subject: str,
    message: str,
    content_pdf: str | None = None,
    name_pdf: str = "reporte.pdf",
) -> dict:
    try:
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")

        if not email_user or not email_password:
            return {
                "success": False,
                "error": "Credenciales no configuradas. Defina EMAIL_USER y EMAIL_PASSWORD.",
            }

        msg = MIMEMultipart()
        msg["From"] = email_user
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain", "utf-8"))

        if content_pdf:
            from utils.general.create_pdf import create_pdf
            pdf_result = create_pdf(content_pdf, name_pdf)
            if not pdf_result.get("success"):
                return {
                    "success": False,
                    "error": f"Error al generar PDF adjunto: {pdf_result.get('error', 'Error desconocido')}",
                }

            pdf_b64 = pdf_result.get("pdf_base64")
            if not pdf_b64:
                return {"success": False, "error": "create_pdf no devolvio pdf_base64."}

            pdf_bytes = base64.b64decode(pdf_b64)
            part = MIMEApplication(pdf_bytes, Name=name_pdf)
            part.add_header("Content-Disposition", "attachment", filename=name_pdf)
            msg.attach(part)

        smtp_server = _guess_smtp_server(email_user)
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        timeout = int(os.getenv("SMTP_TIMEOUT", "15"))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(email_user, email_password)
            server.send_message(msg)

        return {"success": True}

    except smtplib.SMTPAuthenticationError as e:
        return {
            "success": False,
            "error": f"Autenticación SMTP falló: {e}. Verifique credenciales o App Password.",
        }
    except (smtplib.SMTPConnectError, TimeoutError) as e:
        return {"success": False, "error": f"No se pudo conectar al SMTP: {e}"}
    except smtplib.SMTPRecipientsRefused as e:
        return {"success": False, "error": f"Destinatario rechazado: {e}"}
    except smtplib.SMTPException as e:
        return {"success": False, "error": f"Error SMTP: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Error inesperado: {type(e).__name__}: {e}"}
