from types import SimpleNamespace

from chatbot.services import LLMReplyService, RulesReplyService


class FakeModels:
    def __init__(self):
        self.calls = []

    def generate_content(self, model, contents, config=None):
        self.calls.append({"model": model, "contents": contents, "config": config})
        return SimpleNamespace(text="fake answer")


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_rules_service_replies_like_the_rules_brain():
    assert RulesReplyService().reply("hello", []) == "Hi there! How can I help you?"


def test_llm_service_returns_the_model_text():
    service = LLMReplyService(FakeClient(), "some-model", "Be brief.")
    assert service.reply("hi", []) == "fake answer"


def test_llm_service_sends_model_history_and_system_prompt():
    client = FakeClient()
    service = LLMReplyService(client, "some-model", "Be brief.")
    history = [
        {"role": "user", "text": "first"},
        {"role": "bot", "text": "ok"},
    ]

    service.reply("second", history)

    call = client.models.calls[0]
    assert call["model"] == "some-model"
    assert [turn["role"] for turn in call["contents"]] == ["user", "model", "user"]
    assert call["config"] == {"system_instruction": "Be brief."}