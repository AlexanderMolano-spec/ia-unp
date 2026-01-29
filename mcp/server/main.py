from fastmcp import FastMCP

from servers.general import register as register_general

# MCP principal del ecosistema IA-UNP
mcp = FastMCP(
    name="IA-UNP MCP Server",
)

# Register domain-specific tool groups
register_general(mcp)

# Tool mínima de salud (para probar inspector)
@mcp.tool()
def ping() -> str:
    """
    Tool de prueba para validar que el MCP está operativo.
    """
    return "pong"

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )
