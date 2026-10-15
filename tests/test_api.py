from fastapi.testclient import TestClient
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