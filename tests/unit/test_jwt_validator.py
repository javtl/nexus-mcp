import time
<<<<<<< HEAD
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
=======

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

>>>>>>> origin/develop
from nexus_mcp.auth.jwt_validator import JwtTokenValidator, TokenValidationError

ISSUER = "https://auth.example.test"
SCOPE = "nexus/mcp:tools"

<<<<<<< HEAD
=======

>>>>>>> origin/develop
@pytest.fixture(scope="module")
def key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

<<<<<<< HEAD
=======

>>>>>>> origin/develop
@pytest.fixture(scope="module")
def other_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def make_token(private, **overrides):
    now = int(time.time())
    claims = {"iss": ISSUER, "exp": now + 300, "iat": now, "client_id": "alexa-client", "scope": SCOPE}
    claims.update(overrides)
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode(claims, private, algorithm="RS256")

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def validator(key, **kwargs):
    params = dict(issuer=ISSUER, key_resolver=lambda token: key.public_key(), required_scopes=(SCOPE,))
    params.update(kwargs)
    return JwtTokenValidator(**params)

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_valid_token_is_accepted(key):
    verified = validator(key).validate(make_token(key))
    assert verified.client_id == "alexa-client" and SCOPE in verified.scopes

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_expired_token_is_rejected(key):
    with pytest.raises(TokenValidationError):
        validator(key).validate(make_token(key, exp=int(time.time()) - 10))

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_missing_exp_is_rejected(key):
    with pytest.raises(TokenValidationError):
        validator(key).validate(make_token(key, exp=None))

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_wrong_issuer_is_rejected(key):
    with pytest.raises(TokenValidationError):
        validator(key).validate(make_token(key, iss="https://evil.example"))

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_token_signed_with_another_key_is_rejected(key, other_key):
    with pytest.raises(TokenValidationError):
        validator(key).validate(make_token(other_key))

<<<<<<< HEAD
def test_missing_required_scope_is_rejected(key):
=======

def test_missing_scope_is_rejected(key):
>>>>>>> origin/develop
    with pytest.raises(TokenValidationError) as info:
        validator(key).validate(make_token(key, scope="other/scope"))
    assert str(info.value) == "InsufficientScope"

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_unsigned_alg_none_token_is_rejected(key):
    unsigned = jwt.encode({"iss": ISSUER, "exp": int(time.time()) + 300}, None, algorithm="none")
    with pytest.raises(TokenValidationError):
        validator(key).validate(unsigned)

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_garbage_token_is_rejected(key):
    with pytest.raises(TokenValidationError):
        validator(key).validate("not-a-jwt")

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_audience_is_enforced_only_when_configured(key):
    token_without_aud = make_token(key)
    assert validator(key).validate(token_without_aud)
    with pytest.raises(TokenValidationError):
        validator(key, audience="https://nexus.example/mcp").validate(token_without_aud)
    ok = make_token(key, aud="https://nexus.example/mcp")
    assert validator(key, audience="https://nexus.example/mcp").validate(ok)

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_scope_list_claim_is_supported(key):
    token = make_token(key, scope=None, scp=[SCOPE])
    assert validator(key).validate(token).scopes == (SCOPE,)

<<<<<<< HEAD
=======

>>>>>>> origin/develop
def test_error_never_contains_the_token(key):
    bad = make_token(key, iss="https://evil.example")
    with pytest.raises(TokenValidationError) as info:
        validator(key).validate(bad)
<<<<<<< HEAD
    assert bad not in str(info.value)

def test_accepted_scopes_means_any_of(key):
    v = validator(key, required_scopes=(), accepted_scopes=("mcp:service", "mcp:tools"))
    assert v.validate(make_token(key, scope="mcp:service"))
    assert v.validate(make_token(key, scope="other mcp:tools"))
    with pytest.raises(TokenValidationError):
        v.validate(make_token(key, scope="other/scope"))

def test_required_scopes_still_mean_all_of(key):
    v = validator(key, required_scopes=("a", "b"))
    assert v.validate(make_token(key, scope="a b c"))
    with pytest.raises(TokenValidationError):
        v.validate(make_token(key, scope="a"))
=======
    assert bad not in str(info.value)
>>>>>>> origin/develop
