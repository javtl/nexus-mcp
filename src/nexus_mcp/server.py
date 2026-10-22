"""MCP entry point. Thin adapters: translate MCP calls into gateway calls.
Decisions (authorization) and execution live elsewhere."""

from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer
from pydantic import AnyHttpUrl

from nexus_mcp.auth import build_token_verifier
from nexus_mcp.config import load_settings, require_auth_settings
from nexus_mcp.gateway import GatewayResult, Outcome, build_default_gateway

# Carga de configuración y aplicación estricta de fail-closed
_settings = load_settings()
require_auth_settings(_settings)

_gateway = build_default_gateway(_settings)

# Inicialización del servidor MCP con el verificador de tokens de autenticación
mcp = MCPServer(
    "nexus-mcp",
    token_verifier=build_token_verifier(_settings),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(_settings.auth_issuer_url),
        resource_server_url=AnyHttpUrl(_settings.public_url),
        required_scopes=list(_settings.auth_required_scopes) or None,
    ),
)


def _to_mcp(result: GatewayResult) -> dict:
    if result.outcome is Outcome.EXECUTED:
        return result.result  # type: ignore[return-value]
    raise RuntimeError(result.message)


@mcp.tool()
def get_customer(customer_id: int) -> dict:
    """Retrieve a customer's profile by customer ID. Read-only."""
    return _to_mcp(_gateway.call("get_customer", {"customer_id": customer_id}))


@mcp.tool()
def create_order(customer_id: int, items: list[dict]) -> dict:
    """Create a new order for a customer. Each item has 'sku' and 'quantity'."""
    return _to_mcp(_gateway.call("create_order", {"customer_id": customer_id, "items": items}))


@mcp.tool()
def cancel_order(order_id: int) -> dict:
    """Cancel an existing order by order ID. Destructive action."""
    return _to_mcp(_gateway.call("cancel_order", {"order_id": order_id}))


if __name__ == "__main__":
    mcp.run(transport="streamable-http")