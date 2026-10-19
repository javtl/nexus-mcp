"""MCP entry point. Thin adapters: translate MCP calls into gateway calls.
Decisions (authorization) and execution live elsewhere."""

from mcp.server.mcpserver import MCPServer  # como en tu server.py actual

from nexus_mcp.config import load_settings
from nexus_mcp.gateway import GatewayResult, Outcome, build_default_gateway

_settings = load_settings()
_gateway = build_default_gateway(_settings)

mcp = MCPServer("nexus-mcp")


def _to_mcp(result: GatewayResult) -> dict:
    if result.outcome is Outcome.EXECUTED:
        return result.result  # type: ignore[return-value]
    # DENIED or FAILED. [?] D3-2: how should the SDK 2.3.0 report a tool error?
    # Option 1 (preferred if the Inspector shows isError=true with this message):
    raise RuntimeError(result.message)
    # Option 2 (fallback): return {"status": "denied", "reason": result.message, "request_id": result.request_id}


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
    mcp.run(transport="streamable-http")  # conserva tu llamada actual si ya funciona