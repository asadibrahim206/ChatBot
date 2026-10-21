import pytest

from chatbot.dependencies import get_reply_service
from chatbot.errors import LLMConfigurationError
from chatbot.services import LLMReplyService, RulesReplyService


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