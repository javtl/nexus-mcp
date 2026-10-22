
from __future__ import annotations

from typing import Any

from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError


class JwksKeyResolver:
    """Resolve JWT signing keys from a JWKS endpoint."""

    def __init__(
        self,
        jwks_url: str,
        *,
        cache_keys: bool = True,
        lifespan: int = 300,
        timeout: float = 5.0,
    ) -> None:
        if not jwks_url:
            raise ValueError("jwks_url must not be empty")

        if lifespan < 0:
            raise ValueError("lifespan must not be negative")

        if timeout <= 0:
            raise ValueError("timeout must be positive")

        self._client = PyJWKClient(
            jwks_url,
            cache_keys=cache_keys,
            lifespan=lifespan,
            timeout=timeout,
        )

    def get_signing_key(self, token: str) -> Any:
        """Return the signing key corresponding to the JWT's kid."""
        try:
            signing_key = self._client.get_signing_key_from_jwt(token)
            return signing_key.key
        except PyJWKClientError:
            raise
