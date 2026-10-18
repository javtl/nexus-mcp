"""Simulated READ tool. No external systems."""

from __future__ import annotations

from .errors import ToolNotFoundError
from .validation import require_positive_int

_CUSTOMERS = {
    1: {"customer_id": 1, "name": "Ada Lovelace", "email": "ada@example.com"},
    2: {"customer_id": 2, "name": "Alan Turing", "email": "alan@example.com"},
}


def get_customer(customer_id: int) -> dict:
    require_positive_int(customer_id, "customer_id")
    customer = _CUSTOMERS.get(customer_id)
    if customer is None:
        raise ToolNotFoundError(f"customer {customer_id} not found")
    return dict(customer)