import os


def get_db_path() -> str:
    return os.getenv("CHATBOT_DB", "chatbot.db")

def get_brain_name() -> str:
    return os.getenv("CHATBOT_BRAIN", "llm")


def get_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-flash-latest")