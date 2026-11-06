import psycopg
import pytest

from chatbot.postgres_store import PostgresConversationStore


@pytest.fixture
def database_url(migrated_database_url):
    return migrated_database_url


@pytest.fixture
def store(database_url):
    store = PostgresConversationStore(database_url)
    yield store
    store.close()


@pytest.fixture
def session_id():
    return "session-1"


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
    assert store.get_history("another-session") == []


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


def test_store_does_not_create_tables_itself(scratch_database_url):
    store = PostgresConversationStore(scratch_database_url)
    store.close()

    with psycopg.connect(scratch_database_url) as connection:
        tables = connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        ).fetchall()
    assert tables == []