import psycopg
import pytest
from dotenv import dotenv_values

from chatbot.config import ENV_FILE


def test_can_connect_to_postgres():
    url = dotenv_values(ENV_FILE).get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is not set in .env")

    with psycopg.connect(url, connect_timeout=3) as connection:
        assert connection.execute("select 1").fetchone() == (1,)