import sqlite3
import threading

class ConversationStore:
    def __init__(self, db_path: str = ":memory:"):
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def add_message(self, session_id: str, role: str, text: str) -> None:
        with self._lock:
            self._connection.execute(
                "INSERT INTO messages (session_id, role, text) VALUES (?, ?, ?)",
                (session_id, role, text),
            )
            self._connection.commit()

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT role, text FROM messages WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
        return [{"role": role, "text": text} for role, text in rows]

