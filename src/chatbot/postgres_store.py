from psycopg_pool import ConnectionPool

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS messages_session_idx ON messages (session_id, id)
"""


class PostgresConversationStore:
    def __init__(self, database_url: str, max_connections: int = 5):
        self._pool = ConnectionPool(
            database_url,
            min_size=1,
            max_size=max_connections,
            open=True,
        )
        self._pool.wait(timeout=10)
        with self._pool.connection() as connection:
            connection.execute(CREATE_TABLE)
            connection.execute(CREATE_INDEX)

    def add_message(self, session_id: str, role: str, text: str) -> None:
        with self._pool.connection() as connection:
            connection.execute(
                "INSERT INTO messages (session_id, role, text) VALUES (%s, %s, %s)",
                (session_id, role, text),
            )

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        with self._pool.connection() as connection:
            rows = connection.execute(
                "SELECT role, text FROM messages WHERE session_id = %s ORDER BY id",
                (session_id,),
            ).fetchall()
        return [{"role": role, "text": text} for role, text in rows]

    def close(self) -> None:
        self._pool.close()