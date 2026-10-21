import pytest
from fastapi.testclient import TestClient

from chatbot.dependencies import get_reply_service, get_store
from chatbot.errors import (
    LLMConfigurationError,
    LLMRateLimitError,
    LLMUnavailableError,
)
from chatbot.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_returns_reply():
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json()["reply"] == "Hi there! How can I help you?"

def test_chat_rejects_missing_message():
    response = client.post("/chat", json={})
    assert response.status_code == 422


def test_chat_rejects_empty_message():
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422

def test_chat_creates_session_id_when_missing():
    response = client.post("/chat", json={"message": "hello"})
    assert response.json()["session_id"]


def test_chat_keeps_given_session_id():
    response = client.post("/chat", json={"message": "hello", "session_id": "abc"})
    assert response.json()["session_id"] == "abc"

def test_chat_saves_messages_in_history():
    client.post("/chat", json={"message": "hello", "session_id": "history-test"})
    assert get_store().get_history("history-test") == [
        {"role": "user", "text": "hello"},
        {"role": "bot", "text": "Hi there! How can I help you?"},
    ]

def test_history_endpoint_returns_saved_messages():
    client.post("/chat", json={"message": "hello", "session_id": "endpoint-test"})
    response = client.get("/history/endpoint-test")
    assert response.status_code == 200
    assert response.json() == {
        "session_id": "endpoint-test",
        "messages": [
            {"role": "user", "text": "hello"},
            {"role": "bot", "text": "Hi there! How can I help you?"},
        ],
    }


def test_history_of_unknown_session_is_empty():
    response = client.get("/history/nobody")
    assert response.status_code == 200
    assert response.json() == {"session_id": "nobody", "messages": []}

def test_chat_uses_history():
    client.post("/chat", json={"message": "hello", "session_id": "memory-use"})
    response = client.post(
        "/chat", json={"message": "what did I say?", "session_id": "memory-use"}
    )
    assert response.json()["reply"] == 'You said: "hello"'


def test_chat_page_is_served():
    response = client.get("/ui")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_chat_page_has_input_and_send_button():
    html = client.get("/ui").text
    assert 'id="messages"' in html
    assert 'id="message-input"' in html
    assert 'id="send-button"' in html

def test_chat_page_talks_to_the_api():
    html = client.get("/ui").text
    assert 'fetch("/chat"' in html
    assert "session_id" in html


class FakeService:
    def __init__(self, reply_text="fake answer"):
        self.reply_text = reply_text
        self.calls = []

    def reply(self, message, history):
        self.calls.append({"message": message, "history": history})
        return self.reply_text


class BrokenService:
    def __init__(self, error):
        self.error = error

    def reply(self, message, history):
        raise self.error


@pytest.fixture
def override_service():
    def _override(service):
        app.dependency_overrides[get_reply_service] = lambda: service

    yield _override
    app.dependency_overrides.clear()


def test_chat_uses_the_injected_service(override_service):
    service = FakeService("fake answer")
    override_service(service)

    response = client.post("/chat", json={"message": "hi", "session_id": "di-test"})

    assert response.json()["reply"] == "fake answer"
    assert service.calls == [{"message": "hi", "history": []}]


def test_chat_passes_saved_history_to_the_service(override_service):
    service = FakeService()
    override_service(service)

    client.post("/chat", json={"message": "first", "session_id": "di-history"})
    client.post("/chat", json={"message": "second", "session_id": "di-history"})

    assert service.calls[1]["history"] == [
        {"role": "user", "text": "first"},
        {"role": "bot", "text": "fake answer"},
    ]


@pytest.mark.parametrize(
    "error, status, code",
    [
        (LLMUnavailableError(), 503, "llm_unavailable"),
        (LLMRateLimitError(), 429, "llm_rate_limited"),
        (LLMConfigurationError(), 500, "llm_misconfigured"),
    ],
)
def test_llm_errors_become_json_responses(override_service, error, status, code):
    override_service(BrokenService(error))
    session_id = f"err-{code}"

    response = client.post("/chat", json={"message": "hi", "session_id": session_id})

    assert response.status_code == status
    body = response.json()["error"]
    assert set(body) == {"code", "message", "request_id"}
    assert body["code"] == code
    assert body["message"] == error.message
    assert get_store().get_history(session_id) == []
    assert body["request_id"] == response.headers["x-request-id"]

def test_missing_api_key_gives_configuration_error_json(monkeypatch):
    monkeypatch.setenv("CHATBOT_BRAIN", "llm")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = client.post("/chat", json={"message": "hi", "session_id": "no-key"})

    assert response.status_code == 500
    body = response.json()["error"]
    assert body["code"] == "llm_misconfigured"
    assert body["request_id"] == response.headers["x-request-id"]
    assert get_store().get_history("no-key") == []