"""Spike del Día 1: servidor MCP mínimo por Streamable HTTP.

NO contiene autorización, autenticación ni auditoría todavía.
Se reescribe en NX-01 (Día 2).
"""

from mcp.server.fastmcp import FastMCP  # SDK 1.x. En 2.x: ver ejemplo oficial.

mcp = FastMCP("nexus-mcp")


@mcp.tool()
def ping() -> str:
    """Tool de prueba para verificar que el servidor responde."""
    return "pong"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")