"""Small shared input checks for tools."""

from __future__ import annotations

from .errors import ToolInputError


def require_positive_int(value: object, name: str) -> int:
    # bool is a subclass of int in Python, so reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ToolInputError(f"{name} must be a positive integer")
    return value