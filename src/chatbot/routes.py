from uuid import uuid4

from fastapi import APIRouter, status

from chatbot.dependencies import ReplyServiceDep, StoreDep
from chatbot.schemas import ChatRequest, ChatResponse, HistoryResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat(request: ChatRequest, service: ReplyServiceDep, store: StoreDep):
    session_id = request.session_id or str(uuid4())

    history = store.get_history(session_id)
    reply = service.reply(request.message, history)

    store.add_message(session_id, "user", request.message)
    store.add_message(session_id, "bot", reply)

    return ChatResponse(reply=reply, session_id=session_id)


@router.get(
    "/history/{session_id}",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
)
def read_history(session_id: str, store: StoreDep):
    return HistoryResponse(
        session_id=session_id,
        messages=store.get_history(session_id),
    )