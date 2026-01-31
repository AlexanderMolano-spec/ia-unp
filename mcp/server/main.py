from fastmcp import FastMCP
import sys

# 1. CONFIGURACIÓN Y SERVIDORES GENERALES
try:
    from core import config
    from servers.general import register as register_general
    
    # Validar configuración antes de exponer el servidor
    config.validate()
except ImportError as e:
    print(f"[FATAL] Error cargando 'core' o 'servers': {e}", file=sys.stderr)
    sys.exit(1)

# 2. IMPORTAR LÓGICA DE AQUA 
try:
    from tools.aqua.investigar_objetivo import logic_investigar_objetivo
    from tools.aqua.consultar_rag import logic_consultar_rag
    from tools.aqua.consultar_conocimiento import logic_consultar_conocimiento
    from tools.aqua.reportar_objetivo import logic_reportar_objetivo
    from tools.aqua.evaluar_hechos import logic_evaluar_hechos
    
except ImportError as e:
    print(f"[FATAL] Error crítico importando lógica de Aqua: {e}", file=sys.stderr)
    sys.exit(1)

# 3. IMPORTAR LÓGICA GENERAL
try:
    from tools.general.send_email import logic_send_email_report
    from tools.general.create_pdf import logic_create_pdf
    from tools.general.web_spider import logic_web_spider
    
except ImportError as e:
    print(f"[FATAL] Error crítico importando lógica General: {e}", file=sys.stderr)
    sys.exit(1)

# --- SERVIDOR ---
# MCP principal del ecosistema IA-UNP
mcp = FastMCP(
    name="IA-UNP MCP Server",
)

# Registros
register_general(mcp)

@mcp.tool()
def investigar_objetivo_unp(objetivo: str) -> str:
    """[AQUA - EXTERNO] Investiga un objetivo en Internet y guarda el reporte."""
    return logic_investigar_objetivo(objetivo)

@mcp.tool()
def consultar_rag(consulta: str) -> str:
    """[AQUA - INTERNO] Busca antecedentes en la base de datos interna (RAG)."""
    return logic_consultar_rag(consulta)

@mcp.tool()
def consultar_conocimiento(pregunta: str) -> str:
    """[AQUA - ANALÍTICA] Realiza consultas SQL sobre métricas de investigación usando lenguaje natural."""
    return logic_consultar_conocimiento(pregunta)

@mcp.tool()
def reportar_objetivo(objetivo: str) -> str:
    """[AQUA - REPORTES] Genera un informe ejecutivo consolidado sobre un objetivo de interés."""
    return logic_reportar_objetivo(objetivo)

@mcp.tool(name="evaluar_hechos_victimizantes")
def evaluar_hechos_victimizantes(objetivo: str) -> str:
    """[AQUA - FORENSE] Realiza una auditoría forense sobre los riesgos detectados, verificando denuncias formales, evidencia física y corroboración en múltiples fuentes."""
    return logic_evaluar_hechos(objetivo)

# --- GENERAL TOOLS ---

@mcp.tool(name="send_email_report")
async def send_email_report(
    email: str,
    subject: str,
    message: str,
    content_pdf: str = None,
    name_pdf: str = "reporte.pdf"
) -> dict:
    """[GENERAL] Envia un correo electronico con opcion de adjuntar un PDF generado desde HTML."""
    return await logic_send_email_report(email, subject, message, content_pdf, name_pdf)

@mcp.tool(name="create_pdf")
async def create_pdf(html: str, filename: str = "reporte.pdf") -> dict:
    """[GENERAL] Crea un PDF a partir de HTML y retorna los datos para descarga."""
    return await logic_create_pdf(html, filename)

@mcp.tool(name="web_spider")
async def web_spider(
    urls: list[str],
    keywords: list[str],
    deep_search: bool = True,
    max_links_per_page: int = None,
    date_from: str = None,
    date_to: str = None,
    months_back: int = 6
) -> dict:
    """[GENERAL] Busqueda en prensa: visita URLs, extrae enlaces, y busca palabras clave. Filtra por rango de fechas (default: ultimos 6 meses)."""
    return await logic_web_spider(urls, keywords, deep_search, max_links_per_page, date_from, date_to, months_back)

@mcp.tool()
def ping() -> str:
    return "pong - IA-UNP Online"

if __name__ == "__main__":
    # Correr servidor MCP (Transporte HTTP por defecto en main)
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")