from fastmcp import FastMCP
import sys

# 1. IMPORTAR REGISTRADORES GENERALES
try:
    from servers.general import register as register_general
except ImportError:
    def register_general(m): pass

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

# --- SERVIDOR ---
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

@mcp.tool()
def ping() -> str:
    return "pong - IA-UNP Online"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")