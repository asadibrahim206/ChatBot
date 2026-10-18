ROLE_MAP = {"user": "user", "bot": "model"}
class LLMError(Exception):
    """Raised when the LLM call fails or returns nothing."""

def build_contents(user_input: str, history: list[dict[str, str]] | None = None) -> list[dict]:
    contents = []
    for message in history or []:
        contents.append(
            {"role": ROLE_MAP[message["role"]], "parts": [{"text": message["text"]}]}
        )
    contents.append({"role": "user", "parts": [{"text": user_input}]})
    return contents


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
        raise LLMError("The LLM request failed.") from exc

    if not response.text:
        raise LLMError("The LLM returned an empty reply.")
    return response.text


