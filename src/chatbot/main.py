from uuid import uuid4

from fastapi import FastAPI

from chatbot.bot import get_reply
from chatbot.memory import ConversationStore
from chatbot.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Chatbot API")
store = ConversationStore()


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid4())
    reply = get_reply(request.message)

    store.add_message(session_id, "user", request.message)
    store.add_message(session_id, "bot", reply)

    return ChatResponse(reply=reply, session_id=session_id)