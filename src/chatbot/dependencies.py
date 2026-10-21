from functools import cache
from typing import Annotated

from fastapi import Depends

from chatbot.config import get_api_key, get_brain_name, get_db_path, get_model
from chatbot.errors import LLMConfigurationError
from chatbot.memory import ConversationStore
from chatbot.services import LLMReplyService, ReplyService, RulesReplyService
from dotenv import load_dotenv

load_dotenv()


@cache
def make_client():
    from google import genai

    api_key = get_api_key()
    if not api_key:
        raise LLMConfigurationError() from ValueError("GOOGLE_API_KEY is not set")
    return genai.Client(api_key=api_key)


@cache
def get_store() -> ConversationStore:
    return ConversationStore(get_db_path())


def get_reply_service() -> ReplyService:
    if get_brain_name() == "rules":
        return RulesReplyService()
    return LLMReplyService(make_client(), get_model())


ReplyServiceDep = Annotated[ReplyService, Depends(get_reply_service)]
StoreDep = Annotated[ConversationStore, Depends(get_store)]