"""Application settings read from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    public_url: str | None
    audit_file_path: str
    # New fields have defaults so existing tests that build Settings keep working.
    auth_issuer_url: str | None = None
    auth_jwks_url: str | None = None
    auth_audience: str | None = None
    auth_required_scopes: tuple[str, ...] = ()
    auth_accepted_scopes: tuple[str, ...] = ()  # NUEVO: scopes alternativos (ej. mcp:service)


def _split(value: str | None) -> tuple[str, ...]:
    return tuple(part for part in (value or "").replace(",", " ").split() if part)


def load_settings() -> Settings:
    return Settings(
        host=os.environ.get("NEXUS_HOST", "127.0.0.1"),
        # Many hosts provide the port through PORT.
        port=int(os.environ.get("NEXUS_PORT") or os.environ.get("PORT") or "8000"),
        public_url=os.environ.get("NEXUS_PUBLIC_URL") or None,
        audit_file_path=os.environ.get("AUDIT_FILE_PATH", "data/audit.jsonl"),
        auth_issuer_url=os.environ.get("AUTH_ISSUER_URL") or None,
        auth_jwks_url=os.environ.get("AUTH_JWKS_URL") or None,
        auth_audience=os.environ.get("AUTH_AUDIENCE") or None,
        auth_required_scopes=_split(os.environ.get("AUTH_REQUIRED_SCOPES")),
        auth_accepted_scopes=_split(os.environ.get("AUTH_ACCEPTED_SCOPES")),  # NUEVO
    )


def require_auth_settings(settings: Settings) -> None:
    """Fail closed: the server must not start without authentication configured."""
    missing = [
        name
        for name, value in (
            ("NEXUS_PUBLIC_URL", settings.public_url),
            ("AUTH_ISSUER_URL", settings.auth_issuer_url),
            ("AUTH_JWKS_URL", settings.auth_jwks_url),
        )
        if not value
    ]
    if missing:
        raise RuntimeError("Authentication is not configured. Missing: " + ", ".join(missing))