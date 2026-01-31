"""General-domain tools for the IA-UNP MCP server."""

from datetime import datetime, timezone
from fastmcp import FastMCP

from utils.general.send_email_report import send_report_email
from utils.general.create_pdf import create_pdf
from utils.general.web_spider import web_filter


def register(mcp: FastMCP) -> None:
    """Register tools that expose general-purpose capabilities."""

    @mcp.tool(name="get_current_date")
    def get_current_date() -> str:
        """Return the current date in ISO-8601 format using UTC."""

        return datetime.now(timezone.utc).date().isoformat()

    @mcp.tool(name="send_email_report", tags=["GENERAL"])
    def send_email_report_tool(
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
            content_pdf: Contenido HTML para generar el PDF adjunto (opcional)
            name_pdf: Nombre del archivo PDF adjunto (opcional, default: "reporte.pdf")
        
        Returns:
            dict: Diccionario con:
                - "success": bool - True si el correo se envio correctamente
                - "error": str - Mensaje de error (si success=False)
        """
        return send_report_email(email, subject, message, content_pdf, name_pdf)

    @mcp.tool(name="create_pdf", tags=["GENERAL"])
    def create_pdf_tool(html: str, filename: str = "reporte.pdf") -> dict:
        """
        Crea un PDF a partir de HTML y retorna los datos para descarga.
        
        Args:
            html: HTML a convertir a PDF
            filename: Nombre del archivo PDF (opcional, default: "reporte.pdf")
        
        Returns:
            dict: Diccionario con:
                - "success": bool - True si se creó correctamente
                - "pdf_base64": str - Contenido del PDF codificado en base64 (si success=True)
                - "filename": str - Nombre del archivo PDF
                - "mime_type": str - Tipo MIME del archivo ("application/pdf")
                - "error": str - Mensaje de error (si success=False)
        
        Ejemplo de uso desde cliente MCP:
            El cliente recibirá un dict con pdf_base64 que puede decodificar y guardar.
        """
        return create_pdf(html, filename)

    @mcp.tool(name="web_spider", tags=["GENERAL"])
    def web_spider_tool(
        urls: list[str],
        keywords: list[str],
        deep_search: bool = True,
        max_links_per_page: int = None
    ) -> dict:
        """
        Busqueda en prensa: visita URLs, extrae enlaces, y busca multiples palabras clave
        en titulo, descripcion, URL y TODO el texto de la pagina.
        
        Args:
            urls: Lista de URLs iniciales a visitar
            keywords: Lista de palabras clave para buscar (ej: ["corrupcion", "gobierno", "investigacion"])
            deep_search: Si True, visita cada enlace encontrado para extraer su contenido
            max_links_per_page: Maximo de enlaces a analizar por pagina (None = sin limite)
        
        Returns:
            dict: Diccionario con:
                - "success": bool
                - "keywords_used": list - Palabras clave utilizadas
                - "source_pages": dict - Informacion de las paginas fuente
                - "analyzed_links": list - Lista de todos los enlaces analizados
                - "matching_urls": list - Lista final de URLs con coincidencias
                - "summary": dict - Resumen de resultados
        """
        return web_filter(urls, keywords, deep_search, max_links_per_page)
