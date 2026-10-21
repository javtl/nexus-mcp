"""Smoke/demo client: obtains a token (client_credentials) and exercises the three tools.
Never prints the token. Usage: NEXUS_MCP_URL=https://host/mcp python scripts/mcp_smoke.py"""

import asyncio
import os
import sys

import httpx
from mcp import ClientSession                                   # [?] verify in SDK 2.3.0
from mcp.client.streamable_http import streamable_http_client   # [?] name taken from the SDK docs I could read

CALLS = [
    ("get_customer", {"customer_id": 1}),
    ("create_order", {"customer_id": 1, "items": [{"sku": "A-1", "quantity": 2}]}),
    ("cancel_order", {"order_id": 1042}),   # expected: denied by policy
]


def need(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"Missing environment variable: {name}")
    return value


def fetch_token() -> str:
    data = {"grant_type": "client_credentials"}
    if os.environ.get("AUTH_SCOPE"):
        data["scope"] = os.environ["AUTH_SCOPE"]
    if os.environ.get("AUTH_RESOURCE"):          # RFC 8707, if the provider supports it
        data["resource"] = os.environ["AUTH_RESOURCE"]
    response = httpx.post(
        need("AUTH_TOKEN_URL"),
        data=data,
        auth=(need("AUTH_CLIENT_ID"), need("AUTH_CLIENT_SECRET")),   # [?] some providers want credentials in the body
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


async def main() -> None:
    url = need("NEXUS_MCP_URL")
    headers = {"Authorization": f"Bearer {fetch_token()}"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        async with streamable_http_client(url, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print("tools:", [tool.name for tool in tools.tools])
                for name, arguments in CALLS:
                    result = await session.call_tool(name, arguments)
                    texts = [getattr(item, "text", str(item)) for item in result.content]
                    print(f"{name:13} isError={result.isError} -> {texts}")


if __name__ == "__main__":
    asyncio.run(main())