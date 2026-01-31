"""General-domain tools for the IA-UNP MCP server."""

from datetime import datetime, timezone
from fastmcp import FastMCP
from utils.send_report_email import utils_send_report_email


def register(mcp: FastMCP) -> None:
    """Register tools that expose general-purpose capabilities."""

    @mcp.tool(name="get_current_date")
    def get_current_date() -> str:
        """Return the current date in ISO-8601 format using UTC."""

        return datetime.now(timezone.utc).date().isoformat()

    # Envio de correo electronico
    @mcp.tool(tags=["GENERAL"])
    def send_email(
        email: str,
        subject: str,
        message: str,
        content_pdf: str | None = None,
        name_pdf: str = "reporte.pdf",
    ) -> dict:
        """
        Envia un correo electronico con opcion de adjuntar un PDF generado desde HTML.
        
        Args:
            email: Direccion de correo del destinatario
            subject: Asunto del correo
            message: Cuerpo del mensaje en texto plano
            content_pdf: Contenido HTML para generar el PDF adjunto (opcional)
            name_pdf: Nombre del archivo PDF adjunto (opcional, default: "reporte.pdf")
        
        Returns:
            dict: Diccionario con:
                - "success": bool - True si el correo se envio correctamente
                - "error": str - Mensaje de error (si success=False)
        """
        return utils_send_report_email(email, subject, message, content_pdf, name_pdf)
