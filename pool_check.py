import logging
import time

import psycopg
from dotenv import dotenv_values
from psycopg_pool import ConnectionPool

from chatbot.config import ENV_FILE

logging.basicConfig(level=logging.WARNING)
url = dotenv_values(ENV_FILE)["DATABASE_URL"]

targets = [
    ("localhost", url),
    ("127.0.0.1", url.replace("@localhost:", "@127.0.0.1:")),
]

for label, target in targets:
    try:
        start = time.perf_counter()
        with psycopg.connect(target, connect_timeout=20) as connection:
            connection.execute("select 1")
        print(label, "plain connect:", round(time.perf_counter() - start, 2), "s")
    except Exception as exc:
        print(label, "plain connect failed:", type(exc).__name__)

    pool = ConnectionPool(target, min_size=1, max_size=2, open=False)
    try:
        pool.open()
        start = time.perf_counter()
        pool.wait(timeout=20)
        print(label, "pool ready:", round(time.perf_counter() - start, 2), "s")
    except Exception as exc:
        print(label, "pool failed:", type(exc).__name__)
    finally:
        pool.close()