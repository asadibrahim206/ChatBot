from functools import cache

from chatbot.errors import InvalidCredentialsError
from chatbot.security import hash_password, verify_password
from chatbot.tokens import IssuedToken, create_access_token
from chatbot.user_store import User, UserStore


@cache
def _dummy_hash() -> str:
    return hash_password("not-a-real-password")


class AuthService:
    def __init__(self, users: UserStore, secret: str | None, token_minutes: int):
        self._users = users
        self._secret = secret
        self._token_minutes = token_minutes

    def register(self, email: str, password: str) -> User:
        return self._users.create_user(email, hash_password(password))

    def authenticate(self, email: str, password: str) -> IssuedToken:
        user = self._users.get_by_email(email)
        hashed = user.password_hash if user else _dummy_hash()
        password_ok = verify_password(password, hashed)

        if user is None or not password_ok:
            raise InvalidCredentialsError()
        return create_access_token(user.id, self._secret, self._token_minutes)