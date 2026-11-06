from functools import cache
from typing import Annotated

from fastapi import Depends

from chatbot.config import (
    get_api_key,
    get_brain_name,
    get_database_url,
    get_db_path,
    get_model,
)
from chatbot.errors import LLMConfigurationError
from chatbot.memory import ConversationStore, HistoryStore
from chatbot.postgres_store import PostgresConversationStore
from chatbot.services import LLMReplyService, ReplyService, RulesReplyService


@cache
def make_client():
    from google import genai

    api_key = get_api_key()
    if not api_key:
        raise LLMConfigurationError() from ValueError("GOOGLE_API_KEY is not set")
    return genai.Client(api_key=api_key)


@cache
def get_store() -> HistoryStore:
    database_url = get_database_url()
    if database_url:
        return PostgresConversationStore(database_url)
    return ConversationStore(get_db_path())


def close_store() -> None:
    if get_store.cache_info().currsize:
        get_store().close()
        get_store.cache_clear()


def get_reply_service() -> ReplyService:
    if get_brain_name() == "rules":
        return RulesReplyService()
    return LLMReplyService(make_client(), get_model())


ReplyServiceDep = Annotated[ReplyService, Depends(get_reply_service)]
StoreDep = Annotated[HistoryStore, Depends(get_store)]