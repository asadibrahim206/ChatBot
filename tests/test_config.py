from chatbot.config import get_db_path
from chatbot.config import get_brain_name, get_db_path, get_model


def test_db_path_has_a_default(monkeypatch):
    monkeypatch.delenv("CHATBOT_DB", raising=False)
    assert get_db_path() == "chatbot.db"


def test_db_path_comes_from_environment(monkeypatch):
    monkeypatch.setenv("CHATBOT_DB", "custom.db")
    assert get_db_path() == "custom.db"

def test_brain_defaults_to_llm(monkeypatch):
    monkeypatch.delenv("CHATBOT_BRAIN", raising=False)
    assert get_brain_name() == "llm"


def test_brain_comes_from_environment(monkeypatch):
    monkeypatch.setenv("CHATBOT_BRAIN", "rules")
    assert get_brain_name() == "rules"


def test_model_has_a_default(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert get_model() == "gemini-flash-latest"


def test_model_comes_from_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "my-model")
    assert get_model() == "my-model"