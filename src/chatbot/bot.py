import re

RESPONSES = {
    "hello": "Hi there! How can I help you?",
    "how are you": "I'm just code, but I'm running great!",
    "bye": "Goodbye! Have a great day.",

}
FALLBACK = "Sorry, I don't understand that yet."


def get_reply(user_input: str, history: list[dict[str, str]] | None = None) -> str:
    words = re.findall(r"\w+", user_input.lower())
    text = " " + " ".join(words) + " "

    if " what did i say " in text:
        user_texts = [m["text"] for m in (history or []) if m["role"] == "user"]
        if user_texts:
            return f'You said: "{user_texts[-1]}"'
        return "You haven't said anything yet."

    replies = []
    for keyword, reply in RESPONSES.items():
        if f" {keyword} " in text:
            replies.append(reply)

    if replies:
        return " ".join(replies)

    return FALLBACK




