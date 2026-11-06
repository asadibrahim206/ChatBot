import pytest

from chatbot import auth_service
from chatbot.auth_service import AuthService
from chatbot.errors import EmailAlreadyRegisteredError, InvalidCredentialsError
from chatbot.tokens import decode_access_token
from chatbot.user_store import InMemoryUserStore

SECRET = "test-secret-" + "x" * 32
PASSWORD = "correct horse battery"


@pytest.fixture
def users():
    return InMemoryUserStore()


@pytest.fixture
def auth(users):
    return AuthService(users, SECRET, token_minutes=30)


def test_register_stores_a_hash_not_the_password(auth, users):
    user = auth.register("ali@example.com", PASSWORD)

    stored = users.get_by_id(user.id)

    assert stored.password_hash != PASSWORD
    assert stored.password_hash.startswith("$argon2")


def test_registering_the_same_email_twice_fails(auth):
    auth.register("ali@example.com", PASSWORD)

    with pytest.raises(EmailAlreadyRegisteredError):
        auth.register("ALI@example.com", "another password")


def test_authenticate_returns_a_token_for_that_user(auth):
    user = auth.register("ali@example.com", PASSWORD)

    issued = auth.authenticate("ali@example.com", PASSWORD)

    assert decode_access_token(issued.token, SECRET).user_id == user.id


def test_sign_in_ignores_email_case_and_spaces(auth):
    auth.register("ali@example.com", PASSWORD)
    auth.authenticate("  ALI@Example.com ", PASSWORD)


def test_wrong_password_is_rejected(auth):
    auth.register("ali@example.com", PASSWORD)

    with pytest.raises(InvalidCredentialsError):
        auth.authenticate("ali@example.com", "wrong password")


def test_unknown_email_gets_the_same_error_as_a_wrong_password(auth):
    with pytest.raises(InvalidCredentialsError) as unknown:
        auth.authenticate("nobody@example.com", "whatever-password")

    auth.register("ali@example.com", PASSWORD)
    with pytest.raises(InvalidCredentialsError) as wrong:
        auth.authenticate("ali@example.com", "wrong password")

    assert unknown.value.code == wrong.value.code
    assert str(unknown.value) == str(wrong.value)


def test_unknown_email_still_does_a_password_check(auth, monkeypatch):
    calls = []
    original = auth_service.verify_password

    def spy(password, hashed_password):
        calls.append(hashed_password)
        return original(password, hashed_password)

    monkeypatch.setattr(auth_service, "verify_password", spy)

    with pytest.raises(InvalidCredentialsError):
        auth.authenticate("nobody@example.com", "whatever-password")

    assert len(calls) == 1


def test_invalid_credentials_is_a_401():
    error = InvalidCredentialsError()
    assert error.status_code == 401
    assert error.code == "invalid_credentials"