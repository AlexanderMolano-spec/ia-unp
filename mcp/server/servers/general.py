"""General-domain tools for the IA-UNP MCP server."""

from datetime import datetime, timezone
from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register tools that expose general-purpose capabilities."""

    @mcp.tool(name="get_current_date")
    def get_current_date() -> str:
        """Return the current date in ISO-8601 format using UTC."""

        return datetime.now(timezone.utc).date().isoformat()
