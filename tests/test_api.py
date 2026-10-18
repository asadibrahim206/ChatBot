from fastapi.testclient import TestClient
from chatbot.main import app
from chatbot.main import app, store


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
    assert store.get_history("history-test") == [
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
