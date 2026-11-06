from alembic import context
from sqlalchemy import create_engine, pool

from chatbot.config import get_database_url, load_env, to_sqlalchemy_url

config = context.config


def get_url() -> str:
    url = config.attributes.get("database_url")
    if not url:
        load_env()
        url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return to_sqlalchemy_url(url)


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(get_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()