import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values
from psycopg import sql
from sqlalchemy.engine import make_url

from chatbot.config import ENV_FILE

ROOT = Path(__file__).parent.parent

os.environ["CHATBOT_DB"] = ":memory:"
os.environ["CHATBOT_BRAIN"] = "rules"
os.environ.pop("GOOGLE_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("DATABASE_URL", None)


def make_alembic_config(url):
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.attributes["database_url"] = url
    return config


@pytest.fixture
def scratch_database_url():
    base_url = dotenv_values(ENV_FILE).get("DATABASE_URL")
    if not base_url:
        pytest.skip("DATABASE_URL is not set in .env")

    name = f"chatbot_test_{uuid4().hex[:12]}"
    parsed = make_url(base_url)
    admin_url = parsed.set(database="postgres").render_as_string(hide_password=False)
    scratch_url = parsed.set(database=name).render_as_string(hide_password=False)

    with psycopg.connect(admin_url, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    yield scratch_url
    with psycopg.connect(admin_url, autocommit=True) as admin:
        admin.execute(
            sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name))
        )


@pytest.fixture
def migrated_database_url(scratch_database_url):
    command.upgrade(make_alembic_config(scratch_database_url), "head")
    return scratch_database_url