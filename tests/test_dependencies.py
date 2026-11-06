import pytest

from chatbot.dependencies import close_store, get_reply_service, get_store
from chatbot.errors import LLMConfigurationError
from chatbot.memory import ConversationStore
from chatbot.services import LLMReplyService, RulesReplyService


class FakePostgresStore:
    def __init__(self, url):
        self.url = url
        self.closed = False

    def close(self):
        self.closed = True


@pytest.fixture
def fresh_store_cache():
    get_store.cache_clear()
    yield
    get_store.cache_clear()


def test_rules_brain_gives_the_rules_service(monkeypatch):
    monkeypatch.setenv("CHATBOT_BRAIN", "rules")
    assert isinstance(get_reply_service(), RulesReplyService)


def test_llm_brain_gives_the_llm_service(monkeypatch):
    monkeypatch.setenv("CHATBOT_BRAIN", "llm")
    monkeypatch.setattr("chatbot.dependencies.make_client", lambda: object())
    assert isinstance(get_reply_service(), LLMReplyService)


def test_missing_api_key_raises_a_configuration_error(monkeypatch):
    monkeypatch.setenv("CHATBOT_BRAIN", "llm")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(LLMConfigurationError):
        get_reply_service()


def test_sqlite_store_is_used_without_database_url(monkeypatch, fresh_store_cache):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert isinstance(get_store(), ConversationStore)


def test_postgres_store_is_used_with_database_url(monkeypatch, fresh_store_cache):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@127.0.0.1:5433/db")
    monkeypatch.setattr(
        "chatbot.dependencies.PostgresConversationStore", FakePostgresStore
    )

    store = get_store()

    assert isinstance(store, FakePostgresStore)
    assert store.url == "postgresql://u:p@127.0.0.1:5433/db"


def test_store_is_created_only_once(monkeypatch, fresh_store_cache):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_store() is get_store()


def test_close_store_closes_and_forgets_the_store(monkeypatch, fresh_store_cache):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@127.0.0.1:5433/db")
    monkeypatch.setattr(
        "chatbot.dependencies.PostgresConversationStore", FakePostgresStore
    )
    store = get_store()

    close_store()

    assert store.closed
    assert get_store.cache_info().currsize == 0


def test_close_store_does_nothing_when_no_store_exists(fresh_store_cache):
    close_store()