"""Pure JWT access token validation (no MCP SDK, no network in tests).

Answers ONE question: is this token valid for this server?
It does NOT decide whether a tool may run (that is authorization)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import jwt


class TokenValidationError(Exception):
    """The token was rejected. The message never contains the token."""


@dataclass(frozen=True)
class VerifiedToken:
    client_id: str
    scopes: tuple[str, ...]
    expires_at: int


KeyResolver = Callable[[str], Any]


def jwks_key_resolver(jwks_url: str) -> KeyResolver:
    client = jwt.PyJWKClient(jwks_url, cache_keys=True)

    def resolve(token: str) -> Any:
        return client.get_signing_key_from_jwt(token).key

    return resolve


def _extract_scopes(claims: dict[str, Any]) -> tuple[str, ...]:
    raw = claims.get("scope", claims.get("scp", ""))
    if isinstance(raw, str):
        return tuple(raw.split())
    if isinstance(raw, list):
        return tuple(str(item) for item in raw)
    return ()


class JwtTokenValidator:
    def __init__(
        self,
        *,
        issuer: str,
        key_resolver: KeyResolver,
        audience: str | None = None,
        required_scopes: tuple[str, ...] = (),
        algorithms: tuple[str, ...] = ("RS256",),
        leeway_seconds: int = 0,
    ) -> None:
        self._issuer = issuer
        self._key_resolver = key_resolver
        self._audience = audience
        self._required_scopes = required_scopes
        self._algorithms = list(algorithms)   # never include "none" or symmetric algs
        self._leeway = leeway_seconds

    def validate(self, token: str) -> VerifiedToken:
        try:
            key = self._key_resolver(token)
            claims = jwt.decode(
                token,
                key,
                algorithms=self._algorithms,
                issuer=self._issuer,
                audience=self._audience,
                leeway=self._leeway,
                options={"require": ["exp", "iss"], "verify_aud": self._audience is not None},
            )
        except jwt.PyJWTError as exc:
            # Only the exception class name: never the token or claims.
            raise TokenValidationError(type(exc).__name__) from None

        scopes = _extract_scopes(claims)
        if not set(self._required_scopes).issubset(scopes):
            raise TokenValidationError("InsufficientScope")

        client_id = claims.get("client_id") or claims.get("azp") or claims.get("sub")
        if not isinstance(client_id, str) or not client_id:
            raise TokenValidationError("MissingClientIdentity")

        return VerifiedToken(client_id=client_id, scopes=scopes, expires_at=int(claims["exp"]))