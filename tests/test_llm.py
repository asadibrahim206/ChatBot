from types import SimpleNamespace

import pytest

from chatbot.errors import (
    LLMConfigurationError,
    LLMError,
    LLMRateLimitError,
    LLMUnavailableError,
)
from chatbot.llm import ask_llm


class FakeModels:
    def __init__(self):
        self.calls = []
        self.last_config = None

    def generate_content(self, model, contents, config=None):
        self.calls.append({"model": model, "contents": contents})
        self.last_config = config
        return SimpleNamespace(text="fake answer")


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_ask_llm_returns_the_model_text():
    client = FakeClient()
    assert ask_llm("hi", client, "some-model") == "fake answer"


def test_ask_llm_sends_the_prompt_and_model():
    client = FakeClient()
    ask_llm("hi", client, "some-model")
    assert client.models.calls == [
        {
            "model": "some-model",
            "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
        }
    ]


def test_history_is_sent_before_the_new_message():
    client = FakeClient()
    history = [
        {"role": "user", "text": "hello"},
        {"role": "bot", "text": "Hi there!"},
    ]
    ask_llm("what's up", client, "some-model", history)
    assert client.models.calls[0]["contents"] == [
        {"role": "user", "parts": [{"text": "hello"}]},
        {"role": "model", "parts": [{"text": "Hi there!"}]},
        {"role": "user", "parts": [{"text": "what's up"}]},
    ]


def test_system_prompt_is_sent_as_instruction():
    client = FakeClient()
    ask_llm("hi", client, "some-model", system_prompt="Be brief.")
    assert client.models.last_config == {"system_instruction": "Be brief."}


def test_no_system_prompt_sends_no_config():
    client = FakeClient()
    ask_llm("hi", client, "some-model")
    assert client.models.last_config is None


class BrokenModels:
    def generate_content(self, model, contents, config=None):
        raise RuntimeError("boom")


class EmptyModels:
    def generate_content(self, model, contents, config=None):
        return SimpleNamespace(text=None)


def test_ask_llm_wraps_client_errors():
    client = SimpleNamespace(models=BrokenModels())
    with pytest.raises(LLMError):
        ask_llm("hi", client, "some-model")


def test_ask_llm_rejects_empty_replies():
    client = SimpleNamespace(models=EmptyModels())
    with pytest.raises(LLMError):
        ask_llm("hi", client, "some-model")


class FakeAPIError(Exception):
    def __init__(self, code, message=""):
        super().__init__(f"{code} {message}")
        self.code = code
        self.message = message


class RaisingModels:
    def __init__(self, error):
        self.error = error

    def generate_content(self, model, contents, config=None):
        raise self.error


@pytest.mark.parametrize(
    "error, expected",
    [
        (FakeAPIError(429), LLMRateLimitError),
        (FakeAPIError(401), LLMConfigurationError),
        (FakeAPIError(403), LLMConfigurationError),
        (FakeAPIError(404), LLMConfigurationError),
        (
            FakeAPIError(400, "API key not valid. Please pass a valid API key."),
            LLMConfigurationError,
        ),
        (FakeAPIError(500), LLMUnavailableError),
        (FakeAPIError(503), LLMUnavailableError),
        (TimeoutError("too slow"), LLMUnavailableError),
        (RuntimeError("boom"), LLMUnavailableError),
    ],
)
def test_provider_errors_are_translated(error, expected):
    client = SimpleNamespace(models=RaisingModels(error))
    with pytest.raises(expected):
        ask_llm("hi", client, "some-model")