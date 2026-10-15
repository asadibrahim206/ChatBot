from fastapi import FastAPI
from uuid import uuid4
from chatbot.bot import get_reply
from chatbot.schemas import ChatRequest, ChatResponse



app = FastAPI(title="Chatbot API")


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid4())
    return ChatResponse(
        reply=get_reply(request.message),
        session_id=session_id,
    )