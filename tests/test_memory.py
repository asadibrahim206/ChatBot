from chatbot.memory import ConversationStore


def test_new_session_has_empty_history():
    store = ConversationStore()
    assert store.get_history("abc") == []


def test_messages_are_saved_in_order():
    store = ConversationStore()
    store.add_message("abc", "user", "hello")
    store.add_message("abc", "bot", "Hi there!")
    assert store.get_history("abc") == [
        {"role": "user", "text": "hello"},
        {"role": "bot", "text": "Hi there!"},
    ]


def test_sessions_are_kept_separate():
    store = ConversationStore()
    store.add_message("abc", "user", "hello")
    assert store.get_history("xyz") == []


def test_history_survives_a_new_store(tmp_path):
    db_file = str(tmp_path / "test.db")

    first = ConversationStore(db_file)
    first.add_message("abc", "user", "hello")

    second = ConversationStore(db_file)
    assert second.get_history("abc") == [{"role": "user", "text": "hello"}]