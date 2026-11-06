from datetime import datetime, timedelta, timezone

import jwt
import pytest

from chatbot.errors import AuthConfigurationError, NotAuthenticatedError
from chatbot.tokens import create_access_token, decode_access_token

SECRET = "test-secret-" + "x" * 32
OTHER_SECRET = "other-secret-" + "y" * 32


def test_token_round_trip_returns_the_user_id():
    issued = create_access_token(42, SECRET, minutes=30)
    claims = decode_access_token(issued.token, SECRET)

    assert claims.user_id == 42
    assert claims.jti == issued.claims.jti


def test_each_token_has_its_own_id():
    first = create_access_token(1, SECRET, minutes=30)
    second = create_access_token(1, SECRET, minutes=30)
    assert first.claims.jti != second.claims.jti


def test_token_expires_after_the_given_minutes():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    issued = create_access_token(1, SECRET, minutes=30, now=now)
    assert issued.claims.expires_at == now + timedelta(minutes=30)


def test_expired_token_is_rejected():
    long_ago = datetime.now(timezone.utc) - timedelta(hours=2)
    issued = create_access_token(1, SECRET, minutes=30, now=long_ago)

    with pytest.raises(NotAuthenticatedError):
        decode_access_token(issued.token, SECRET)


def test_token_signed_with_another_secret_is_rejected():
    issued = create_access_token(1, OTHER_SECRET, minutes=30)

    with pytest.raises(NotAuthenticatedError):
        decode_access_token(issued.token, SECRET)


def test_garbage_is_rejected():
    with pytest.raises(NotAuthenticatedError):
        decode_access_token("not-a-token", SECRET)


def test_token_with_no_signature_is_rejected():
    unsigned = jwt.encode(
        {"sub": "1", "jti": "x", "exp": 9999999999}, None, algorithm="none"
    )

    with pytest.raises(NotAuthenticatedError):
        decode_access_token(unsigned, SECRET)


def test_token_missing_required_claims_is_rejected():
    token = jwt.encode({"sub": "1"}, SECRET, algorithm="HS256")

    with pytest.raises(NotAuthenticatedError):
        decode_access_token(token, SECRET)


def test_missing_or_short_secret_is_a_configuration_error():
    with pytest.raises(AuthConfigurationError):
        create_access_token(1, None, minutes=30)
    with pytest.raises(AuthConfigurationError):
        create_access_token(1, "short", minutes=30)
    with pytest.raises(AuthConfigurationError):
        decode_access_token("anything", None)


def test_auth_errors_have_the_right_status_codes():
    assert NotAuthenticatedError().status_code == 401
    assert AuthConfigurationError().status_code == 500