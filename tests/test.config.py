from chatbot.config import get_db_path


def test_db_path_has_a_default(monkeypatch):
    monkeypatch.delenv("CHATBOT_DB", raising=False)
    assert get_db_path() == "chatbot.db"


def test_db_path_comes_from_environment(monkeypatch):
    monkeypatch.setenv("CHATBOT_DB", "custom.db")
    assert get_db_path() == "custom.db"