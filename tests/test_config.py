import os

from chatbot.config import (
    get_api_key,
    get_brain_name,
    get_database_url,
    get_db_path,
    get_jwt_secret,
    get_model,
    get_token_minutes,
    load_env,
    to_sqlalchemy_url,
)

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

def test_load_env_reads_values_from_a_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("CHATBOT_TEST_VALUE=from-file\n")
    monkeypatch.setenv("CHATBOT_TEST_VALUE", "placeholder")
    monkeypatch.delenv("CHATBOT_TEST_VALUE")

    load_env(env_file)

    assert os.environ["CHATBOT_TEST_VALUE"] == "from-file"


def test_load_env_does_not_override_the_real_environment(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("CHATBOT_TEST_VALUE=from-file\n")
    monkeypatch.setenv("CHATBOT_TEST_VALUE", "from-shell")

    load_env(env_file)

    assert os.environ["CHATBOT_TEST_VALUE"] == "from-shell"


def test_load_env_with_a_missing_file_is_fine(tmp_path):
    load_env(tmp_path / "does-not-exist.env")


def test_database_url_comes_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    assert get_database_url() == "postgresql://user:pass@localhost:5432/db"


def test_database_url_is_none_when_unset(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url() is None

def test_plain_postgres_url_gets_the_psycopg_driver():
    url = "postgresql://u:p@127.0.0.1:5433/db"
    assert to_sqlalchemy_url(url) == "postgresql+psycopg://u:p@127.0.0.1:5433/db"


def test_url_that_names_a_driver_is_left_alone():
    url = "postgresql+psycopg://u:p@127.0.0.1:5433/db"
    assert to_sqlalchemy_url(url) == url


def test_jwt_secret_comes_from_environment(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "fake-secret-for-tests")
    assert get_jwt_secret() == "fake-secret-for-tests"


def test_jwt_secret_is_none_when_unset(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    assert get_jwt_secret() is None


def test_token_minutes_defaults_to_30(monkeypatch):
    monkeypatch.delenv("ACCESS_TOKEN_MINUTES", raising=False)
    assert get_token_minutes() == 30


def test_token_minutes_comes_from_environment(monkeypatch):
    monkeypatch.setenv("ACCESS_TOKEN_MINUTES", "5")
    assert get_token_minutes() == 5