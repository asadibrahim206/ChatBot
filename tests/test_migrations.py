from pathlib import Path

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).parent.parent


@pytest.fixture
def alembic_config(scratch_database_url):
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.attributes["database_url"] = scratch_database_url
    return config


def table_names(url):
    with psycopg.connect(url) as connection:
        rows = connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        ).fetchall()
    return {row[0] for row in rows}


def column_names(url, table):
    with psycopg.connect(url) as connection:
        rows = connection.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = %s",
            (table,),
        ).fetchall()
    return {row[0] for row in rows}


def test_alembic_can_connect_to_the_database(alembic_config):
    command.current(alembic_config)


def test_upgrade_creates_the_messages_table(alembic_config, scratch_database_url):
    command.upgrade(alembic_config, "head")

    assert "messages" in table_names(scratch_database_url)
    assert column_names(scratch_database_url, "messages") == {
        "id",
        "session_id",
        "role",
        "text",
        "created_at",
    }


def test_downgrade_removes_the_messages_table(alembic_config, scratch_database_url):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")

    assert "messages" not in table_names(scratch_database_url)


def test_migration_can_be_applied_again_after_a_downgrade(
    alembic_config, scratch_database_url
):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")

    assert "messages" in table_names(scratch_database_url)


def test_there_is_a_single_migration_head(alembic_config):
    assert len(ScriptDirectory.from_config(alembic_config).get_heads()) == 1

def test_upgrade_creates_the_users_table(alembic_config, scratch_database_url):
    command.upgrade(alembic_config, "head")

    assert "users" in table_names(scratch_database_url)
    assert column_names(scratch_database_url, "users") == {
        "id",
        "email",
        "password_hash",
        "created_at",
    }


def test_emails_must_be_unique(alembic_config, scratch_database_url):
    command.upgrade(alembic_config, "head")

    with psycopg.connect(scratch_database_url) as connection:
        connection.execute(
            "INSERT INTO users (email, password_hash) VALUES ('a@example.com', 'x')"
        )

    with pytest.raises(psycopg.errors.UniqueViolation):
        with psycopg.connect(scratch_database_url) as connection:
            connection.execute(
                "INSERT INTO users (email, password_hash) VALUES ('a@example.com', 'y')"
            )


def test_downgrading_one_step_removes_users_but_keeps_messages(
    alembic_config, scratch_database_url
):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "-1")

    tables = table_names(scratch_database_url)
    assert "messages" in tables
    assert "users" not in tables