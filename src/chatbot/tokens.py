from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from chatbot.errors import AuthConfigurationError, NotAuthenticatedError

ALGORITHM = "HS256"
MIN_SECRET_LENGTH = 32


@dataclass(frozen=True)
class TokenClaims:
    user_id: int
    jti: str
    expires_at: datetime


@dataclass(frozen=True)
class IssuedToken:
    token: str
    claims: TokenClaims


def _checked_secret(secret: str | None) -> str:
    if not secret or len(secret) < MIN_SECRET_LENGTH:
        raise AuthConfigurationError()
    return secret


def create_access_token(
    user_id: int,
    secret: str | None,
    minutes: int,
    now: datetime | None = None,
) -> IssuedToken:
    secret = _checked_secret(secret)
    issued_at = now or datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=minutes)
    jti = str(uuid4())

    token = jwt.encode(
        {"sub": str(user_id), "jti": jti, "iat": issued_at, "exp": expires_at},
        secret,
        algorithm=ALGORITHM,
    )
    return IssuedToken(token, TokenClaims(user_id, jti, expires_at))


def decode_access_token(token: str, secret: str | None) -> TokenClaims:
    secret = _checked_secret(secret)
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "jti"]},
        )
        return TokenClaims(
            user_id=int(payload["sub"]),
            jti=payload["jti"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise NotAuthenticatedError() from exc