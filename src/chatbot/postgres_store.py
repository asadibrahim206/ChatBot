from psycopg_pool import ConnectionPool


class PostgresConversationStore:
    def __init__(self, database_url: str, max_connections: int = 5):
        self._pool = ConnectionPool(
            database_url,
            min_size=1,
            max_size=max_connections,
            open=True,
        )
        self._pool.wait(timeout=10)

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