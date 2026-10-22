"""Catches import/contract breaks between the pure validator and the SDK adapter."""

from nexus_mcp.auth.jwt_validator import VerifiedToken, jwks_key_resolver  # noqa: F401
from nexus_mcp.auth.verifier import NexusTokenVerifier, build_token_verifier  # noqa: F401
from nexus_mcp.config import Settings


def test_verified_token_has_the_fields_the_adapter_uses():
    token = VerifiedToken(client_id="c", scopes=("s",), expires_at=1)
    assert (token.client_id, token.scopes, token.expires_at) == ("c", ("s",), 1)


def test_verifier_can_be_built_from_settings():
    settings = Settings(
        host="h", port=1, public_url="https://nexus.test", audit_file_path="x",
        auth_issuer_url="https://auth.test/", auth_jwks_url="https://auth.test/.well-known/jwks.json",
        auth_accepted_scopes=("mcp:service",),
    )
    assert build_token_verifier(settings) is not None