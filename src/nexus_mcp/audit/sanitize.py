"""Redacts sensitive values before they reach the audit log."""

from __future__ import annotations

from typing import Any

_SENSITIVE_FRAGMENTS = ("token", "secret", "password", "authorization", "api_key", "private_key")
REDACTED = "[REDACTED]"


def _is_sensitive(key: str) -> bool:
    lowered = key.lower()
    return any(fragment in lowered for fragment in _SENSITIVE_FRAGMENTS)


def sanitize_arguments(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: (REDACTED if isinstance(k, str) and _is_sensitive(k) else sanitize_arguments(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [sanitize_arguments(item) for item in value]
    return value