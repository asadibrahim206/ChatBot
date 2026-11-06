from dataclasses import dataclass
from typing import Protocol

import psycopg
from psycopg_pool import ConnectionPool

from chatbot.errors import EmailAlreadyRegisteredError


@dataclass(frozen=True)
class User:
    id: int
    email: str
    password_hash: str


def normalize_email(email: str) -> str:
    return email.strip().lower()


class UserStore(Protocol):
    def create_user(self, email: str, password_hash: str) -> User: ...

    def get_by_email(self, email: str) -> User | None: ...

    def get_by_id(self, user_id: int) -> User | None: ...

    def close(self) -> None: ...


class InMemoryUserStore:
    def __init__(self):
        self._users: dict[int, User] = {}
        self._next_id = 1

    def create_user(self, email: str, password_hash: str) -> User:
        email = normalize_email(email)
        if self.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError()
        user = User(id=self._next_id, email=email, password_hash=password_hash)
        self._users[user.id] = user
        self._next_id += 1
        return user

    def get_by_email(self, email: str) -> User | None:
        email = normalize_email(email)
        return next((u for u in self._users.values() if u.email == email), None)

    def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def close(self) -> None:
        pass


class PostgresUserStore:
    def __init__(self, database_url: str, max_connections: int = 3):
        self._pool = ConnectionPool(
            database_url,
            min_size=1,
            max_size=max_connections,
            open=True,
        )
        self._pool.wait(timeout=10)

    def create_user(self, email: str, password_hash: str) -> User:
        email = normalize_email(email)
        try:
            with self._pool.connection() as connection:
                row = connection.execute(
                    "INSERT INTO users (email, password_hash) "
                    "VALUES (%s, %s) RETURNING id",
                    (email, password_hash),
                ).fetchone()
        except psycopg.errors.UniqueViolation as exc:
            raise EmailAlreadyRegisteredError() from exc
        return User(id=row[0], email=email, password_hash=password_hash)

    def get_by_email(self, email: str) -> User | None:
        with self._pool.connection() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash FROM users WHERE email = %s",
                (normalize_email(email),),
            ).fetchone()
        return User(*row) if row else None

    def get_by_id(self, user_id: int) -> User | None:
        with self._pool.connection() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash FROM users WHERE id = %s",
                (user_id,),
            ).fetchone()
        return User(*row) if row else None

    def close(self) -> None:
        self._pool.close()