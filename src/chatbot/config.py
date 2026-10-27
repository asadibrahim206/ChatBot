import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def load_env(path: Path | str = ENV_FILE) -> None:
    load_dotenv(path, override=False)


def get_db_path() -> str:
    return os.getenv("CHATBOT_DB", "chatbot.db")


def get_brain_name() -> str:
    return os.getenv("CHATBOT_BRAIN", "llm")


def get_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-flash-latest")


def get_api_key() -> str | None:
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

def get_database_url() -> str | None:
    return os.getenv("DATABASE_URL")