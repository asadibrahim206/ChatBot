from functools import cache
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from chatbot.bot import get_reply
from chatbot.config import get_brain_name, get_db_path, get_model
from chatbot.llm import ask_llm,LLMError
from chatbot.memory import ConversationStore
from chatbot.schemas import ChatRequest, ChatResponse, HistoryResponse
import logging
from functools import cache
from pathlib import Path




app = FastAPI(title="Chatbot API")
store = ConversationStore(get_db_path())


STATIC_DIR = Path(__file__).parent / "static"

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a friendly assistant inside a small chat app. "
    "Keep your answers short and clear."
)


@cache
def make_client():
    from google import genai

    return genai.Client()


def get_brain():
    if get_brain_name() == "rules":
        return get_reply

    client = make_client()
    model = get_model()

    def llm_brain(message, history):
        return ask_llm(message, client, model, history, SYSTEM_PROMPT)

    return llm_brain


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

    history = store.get_history(session_id)
    try:
        reply = get_brain()(request.message, history)
    except LLMError:
        logger.exception("LLM call failed")
        raise HTTPException(
            status_code=502,
            detail="The AI service is unavailable. Please try again.",
        )

    store.add_message(session_id, "user", request.message)
    store.add_message(session_id, "bot", reply)

    return ChatResponse(reply=reply, session_id=session_id)


@app.get("/history/{session_id}", response_model=HistoryResponse)
def read_history(session_id: str):
    return HistoryResponse(
        session_id=session_id,
        messages=store.get_history(session_id),
    )


@app.get("/ui", include_in_schema=False)
def chat_page():
    return FileResponse(STATIC_DIR / "index.html")