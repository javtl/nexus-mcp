"""Simulated WRITE tool. Creates an in-memory order with a deterministic ID."""

from __future__ import annotations

from itertools import count

from .errors import ToolInputError
from .validation import require_positive_int

_FIRST_ORDER_ID = 1001
_order_ids = count(_FIRST_ORDER_ID)


def reset_orders() -> None:
    """Reset the ID counter. Used by tests to keep results deterministic."""
    global _order_ids
    _order_ids = count(_FIRST_ORDER_ID)


def create_order(customer_id: int, items: list[dict]) -> dict:
    require_positive_int(customer_id, "customer_id")
    if not isinstance(items, list) or not items:
        raise ToolInputError("items must be a non-empty list")

    clean_items = []
    for item in items:
        if not isinstance(item, dict):
            raise ToolInputError("each item must be an object")
        sku = item.get("sku")
        if not isinstance(sku, str) or not sku.strip():
            raise ToolInputError("each item needs a non-empty 'sku'")
        quantity = require_positive_int(item.get("quantity"), "quantity")
        clean_items.append({"sku": sku.strip(), "quantity": quantity})

    return {
        "order_id": next(_order_ids),
        "customer_id": customer_id,
        "items": clean_items,
        "status": "CREATED",
    }