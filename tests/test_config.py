from chatbot.config import get_api_key, get_brain_name, get_db_path, get_model


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

def test_api_key_comes_from_google_variable(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-google-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert get_api_key() == "fake-google-key"


def test_api_key_falls_back_to_gemini_variable(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    assert get_api_key() == "fake-gemini-key"


def test_api_key_is_none_when_unset(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert get_api_key() is None