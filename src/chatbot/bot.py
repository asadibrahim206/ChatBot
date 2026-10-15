import re

RESPONSES = {
    "hello": "Hi there! How can I help you?",
    "how are you": "I'm just code, but I'm running great!",
    "bye": "Goodbye! Have a great day.",

}
FALLBACK = "Sorry, I don't understand that yet."


def get_reply(user_input: str) -> str:
    words = re.findall(r"\w+", user_input.lower())
    text = " "+" ".join(words) + " "     #to convert list back to str
    
    replies = []
    for keyword, reply in RESPONSES.items():
        if f" {keyword} " in text:
            replies.append(reply)
    if replies:
        return " ".join(replies)
   
    return FALLBACK


