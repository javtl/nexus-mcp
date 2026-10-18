"""Simulated DESTRUCTIVE tool.

It exists so the system is complete and testable. In the MVP it must NEVER be
invoked through Nexus: the policy returns DENY and the gateway does not call it.
"""

from __future__ import annotations

from .validation import require_positive_int


def cancel_order(order_id: int) -> dict:
    require_positive_int(order_id, "order_id")
    return {"order_id": order_id, "status": "CANCELLED"}