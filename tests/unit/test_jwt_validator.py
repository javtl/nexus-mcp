from __future__ import annotations

import time
import pytest
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from nexus_mcp.auth.jwt_validator import JwtTokenValidator, TokenValidationError


@pytest.fixture
def rsa_key():
    """Genera una clave privada RSA de prueba."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def key(rsa_key):
    """Alias para la clave de prueba."""
    return rsa_key


class MockKeyResolver:
    """Resolvedor de claves simulado para tests unitarios."""
    def __init__(self, private_key):
        self.public_key = private_key.public_key()

    def get_signing_key(self, token: str):
        return self.public_key


def make_token(private_key, scope: str = "", issuer: str = "https://auth.example.com") -> str:
    """Genera un JWT firmado para pruebas."""
    now = time.time()
    payload = {
        "iss": issuer,
        "sub": "user-123",
        "exp": now + 3600,
        "iat": now,
    }
    if scope:
        payload["scope"] = scope
    
    return jwt.encode(payload, private_key, algorithm="RS256")


def validator(private_key, required_scopes=(), accepted_scopes=()):
    """Instancia rápida de JwtTokenValidator para tests."""
    resolver = MockKeyResolver(private_key)
    return JwtTokenValidator(
        issuer="https://auth.example.com",
        key_resolver=resolver,
        required_scopes=required_scopes,
        accepted_scopes=accepted_scopes,
    )


def test_accepted_scopes_means_any_of(key):
    v = validator(key, required_scopes=(), accepted_scopes=("mcp:service", "mcp:tools"))
    assert v.validate(make_token(key, scope="mcp:service"))
    assert v.validate(make_token(key, scope="other mcp:tools"))
    with pytest.raises(TokenValidationError):
        v.validate(make_token(key, scope="other/scope"))