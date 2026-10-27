from uuid import uuid4

import psycopg
import pytest
from dotenv import dotenv_values

from chatbot.config import ENV_FILE
from chatbot.postgres_store import PostgresConversationStore


@pytest.fixture
def database_url():
    url = dotenv_values(ENV_FILE).get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is not set in .env")
    yield url
    with psycopg.connect(url) as connection:
        connection.execute("DELETE FROM messages WHERE session_id LIKE 'pgtest-%'")


@pytest.fixture
def store(database_url):
    store = PostgresConversationStore(database_url)
    yield store
    store.close()


@pytest.fixture
def session_id():
    return f"pgtest-{uuid4()}"


def test_new_session_has_empty_history(store, session_id):
    assert store.get_history(session_id) == []


def test_messages_are_saved_in_order(store, session_id):
    store.add_message(session_id, "user", "hello")
    store.add_message(session_id, "bot", "Hi there!")
    assert store.get_history(session_id) == [
        {"role": "user", "text": "hello"},
        {"role": "bot", "text": "Hi there!"},
    ]


def test_sessions_are_kept_separate(store, session_id):
    store.add_message(session_id, "user", "hello")
    assert store.get_history(f"{session_id}-other") == []


def test_history_survives_a_new_store(database_url, store, session_id):
    store.add_message(session_id, "user", "hello")

    second = PostgresConversationStore(database_url)
    try:
        assert second.get_history(session_id) == [{"role": "user", "text": "hello"}]
    finally:
        second.close()


def test_text_is_stored_exactly_as_sent(store, session_id):
    tricky = "'); DROP TABLE messages; -- سلام 👋"
    store.add_message(session_id, "user", tricky)
    assert store.get_history(session_id) == [{"role": "user", "text": tricky}]