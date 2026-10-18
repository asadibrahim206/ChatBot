from uuid import uuid4

from fastapi import FastAPI

from chatbot.schemas import ChatRequest, ChatResponse, HistoryResponse
from chatbot.bot import get_reply
from chatbot.memory import ConversationStore
from chatbot.schemas import ChatRequest, ChatResponse
from pathlib import Path
from fastapi.responses import FileResponse

app = FastAPI(title="Chatbot API")
store = ConversationStore()

STATIC_DIR = Path(__file__).parent / "static"

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

    history = store.get_history(session_id)
    reply = get_reply(request.message, history)

    store.add_message(session_id, "user", request.message)
    store.add_message(session_id, "bot", reply)

    return ChatResponse(reply=reply, session_id=session_id)

@app.get("/history/{session_id}", response_model=HistoryResponse)
def read_history(session_id: str):
    return HistoryResponse(
        session_id=session_id,
        messages=store.get_history(session_id),
    )

def test_chat_page_is_served():
    response = client.get("/ui")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@app.get("/ui", include_in_schema=False)
def chat_page():
    return FileResponse(STATIC_DIR / "index.html")