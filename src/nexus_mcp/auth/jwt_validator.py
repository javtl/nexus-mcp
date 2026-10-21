
from __future__ import annotations

import logging
from typing import Any, Protocol

import jwt
from jwt.exceptions import PyJWTError
from jwt import PyJWKClient

logger = logging.getLogger(__name__)


class KeyResolver(Protocol):
    """Interface for resolving the signing key associated with a JWT."""

    def get_signing_key(self, token: str) -> str | Any:
        ...


class VerifiedToken:
    """Represents a successfully validated JWT."""

    def __init__(self, claims: dict[str, Any]) -> None:
        self.claims = claims

    @property
    def subject(self) -> str | None:
        value = self.claims.get("sub")
        return value if isinstance(value, str) else None

    @property
    def issuer(self) -> str | None:
        value = self.claims.get("iss")
        return value if isinstance(value, str) else None

    @property
    def scopes(self) -> tuple[str, ...]:
        return _extract_scopes(self.claims)


class TokenValidationError(Exception):
    """Raised when JWT validation fails."""


def _extract_scopes(claims: dict[str, Any]) -> tuple[str, ...]:
    """Extract scopes from either the scope or scp claim."""
    scope_claim = claims.get("scope") or claims.get("scp") or ""

    if isinstance(scope_claim, str):
        return tuple(scope_claim.split())

    if isinstance(scope_claim, list):
        if all(isinstance(scope, str) for scope in scope_claim):
            return tuple(scope_claim)
        return ()

    return ()


class JwtTokenValidator:
    """Validate JWT signatures, standard claims, and authorization scopes."""

    def __init__(
        self,
        *,
        issuer: str,
        key_resolver: KeyResolver,
        audience: str | None = None,
        required_scopes: tuple[str, ...] = (),
        accepted_scopes: tuple[str, ...] = (),
        algorithms: tuple[str, ...] = ("RS256",),
        leeway_seconds: int = 0,
    ) -> None:
        if not issuer:
            raise ValueError("issuer must not be empty")

        if not algorithms:
            raise ValueError("algorithms must not be empty")

        if leeway_seconds < 0:
            raise ValueError("leeway_seconds must not be negative")

        self._issuer = issuer
        self._key_resolver = key_resolver
        self._audience = audience
        self._required_scopes = required_scopes
        self._accepted_scopes = accepted_scopes
        self._algorithms = list(algorithms)
        self._leeway_seconds = leeway_seconds

    def validate(self, token: str) -> VerifiedToken:
        """Validate a JWT and return its verified claims."""
        if not token:
            raise TokenValidationError("Token must not be empty")

        try:
            signing_key = self._key_resolver.get_signing_key(token)

            # PyJWKClient.get_signing_key_from_jwt() returns a PyJWK object.
            # PyJWT.decode() accepts the underlying cryptographic key.
            if hasattr(signing_key, "key"):
                signing_key = signing_key.key

            options = {
                "verify_signature": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_aud": self._audience is not None,
                "require": ["exp", "iss"],
            }

            claims = jwt.decode(
                token,
                key=signing_key,
                algorithms=self._algorithms,
                issuer=self._issuer,
                audience=self._audience,
                options=options,
                leeway=self._leeway_seconds,
            )

        except (PyJWKClientError, PyJWTError) as exc:
            logger.warning("JWT validation failed: %s", exc)
            raise TokenValidationError(
                f"Invalid token: {exc}"
            ) from exc
        except Exception as exc:
            # Key resolvers can also raise implementation-specific errors.
            logger.warning("Signing key resolution failed: %s", exc)
            raise TokenValidationError(
                "Unable to resolve the JWT signing key"
            ) from exc

        scopes = _extract_scopes(claims)
        scope_set = set(scopes)

        # All required scopes must be present.
        missing_scopes = set(self._required_scopes) - scope_set
        if missing_scopes:
            raise TokenValidationError(
                f"Missing required scopes: {sorted(missing_scopes)}"
            )

        # At least one accepted scope must be present when configured.
        if (
            self._accepted_scopes
            and not set(self._accepted_scopes).intersection(scope_set)
        ):
            raise TokenValidationError(
                "None of the accepted scopes are present. "
                f"Accepted: {self._accepted_scopes}, Got: {scopes}"
            )

        return VerifiedToken(claims)
