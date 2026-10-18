"""MCP server entry point. Tools here are PLACEHOLDERS until the gateway
(NX-04, Day 3) wires them through authorization. Nothing executes real logic."""

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("nexus-mcp")


@mcp.tool()
def get_customer(customer_id: int) -> dict:
    """Retrieve a customer's profile by customer ID. Read-only."""
    return {"status": "not_wired"}


@mcp.tool()
def create_order(customer_id: int, items: list[dict]) -> dict:
    """Create a new order for a customer. Each item has 'sku' and 'quantity'."""
    return {"status": "not_wired"}


@mcp.tool()
def cancel_order(order_id: int) -> dict:
    """Cancel an existing order by order ID. Destructive action."""
    return {"status": "not_wired"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")