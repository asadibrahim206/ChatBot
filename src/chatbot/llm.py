from chatbot.errors import (
    LLMConfigurationError,
    LLMError,
    LLMRateLimitError,
    LLMUnavailableError,
)

ROLE_MAP = {"user": "user", "bot": "model"}


def build_contents(
    user_input: str, history: list[dict[str, str]] | None = None
) -> list[dict]:
    contents = []
    for message in history or []:
        contents.append(
            {"role": ROLE_MAP[message["role"]], "parts": [{"text": message["text"]}]}
        )
    contents.append({"role": "user", "parts": [{"text": user_input}]})
    return contents


def classify_error(exc: Exception) -> LLMError:
    code = getattr(exc, "code", None)
    message = str(getattr(exc, "message", "") or "").lower()

    if code == 429:
        return LLMRateLimitError()
    if code in (401, 403, 404) or (code == 400 and "api key" in message):
        return LLMConfigurationError()
    return LLMUnavailableError()


def ask_llm(
    user_input: str,
    client,
    model: str,
    history: list[dict[str, str]] | None = None,
    system_prompt: str | None = None,
) -> str:
    config = {"system_instruction": system_prompt} if system_prompt else None

    try:
        response = client.models.generate_content(
            model=model,
            contents=build_contents(user_input, history),
            config=config,
        )
    except Exception as exc:
        raise classify_error(exc) from exc

    if not response.text:
        raise LLMUnavailableError()
    return response.text