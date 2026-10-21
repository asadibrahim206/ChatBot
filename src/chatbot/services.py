from typing import Protocol

from chatbot.bot import get_reply
from chatbot.llm import ask_llm

DEFAULT_SYSTEM_PROMPT = (
    "You are a friendly assistant inside a small chat app. "
    "Keep your answers short and clear."
)


class ReplyService(Protocol):
    def reply(self, message: str, history: list[dict[str, str]]) -> str: ...


class RulesReplyService:
    def reply(self, message: str, history: list[dict[str, str]]) -> str:
        return get_reply(message, history)


class LLMReplyService:
    def __init__(
        self,
        client,
        model: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        self._client = client
        self._model = model
        self._system_prompt = system_prompt

    def reply(self, message: str, history: list[dict[str, str]]) -> str:
        return ask_llm(
            message,
            self._client,
            self._model,
            history,
            self._system_prompt,
        )