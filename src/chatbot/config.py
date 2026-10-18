import os


def get_db_path() -> str:
    return os.getenv("CHATBOT_DB", "chatbot.db")