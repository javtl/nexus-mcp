"""Adapter between the pure validator and the MCP SDK's TokenVerifier protocol."""

from __future__ import annotations

import asyncio

from mcp.server.auth.provider import AccessToken, TokenVerifier  # [?] verify import path in SDK 2.3.0

from nexus_mcp.config import Settings

from .jwt_validator import JwtTokenValidator, TokenValidationError, jwks_key_resolver


class NexusTokenVerifier(TokenVerifier):
    def __init__(self, validator: JwtTokenValidator) -> None:
        self._validator = validator

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            # PyJWKClient does blocking network I/O: keep it off the event loop.
            verified = await asyncio.to_thread(self._validator.validate, token)
        except TokenValidationError:
            return None   # the SDK turns None into a 401
        return AccessToken(  # [?] check the exact AccessToken fields in SDK 2.3.0
            token=token,
            client_id=verified.client_id,
            scopes=list(verified.scopes),
            expires_at=verified.expires_at,
        )


def build_token_verifier(settings: Settings) -> NexusTokenVerifier:
    validator = JwtTokenValidator(
        issuer=settings.auth_issuer_url,                  # validated by require_auth_settings
        key_resolver=jwks_key_resolver(settings.auth_jwks_url),
        audience=settings.auth_audience,
        required_scopes=settings.auth_required_scopes,
        accepted_scopes=settings.auth_accepted_scopes,    # NUEVO: pasamos los scopes aceptados (ej. mcp:service)
    )
    return NexusTokenVerifier(validator)