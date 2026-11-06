from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from chatbot.config import load_env
from chatbot.dependencies import close_store
from chatbot.error_handlers import register_error_handlers
from chatbot.middleware import register_middleware
from chatbot.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env()
    yield
    close_store()


app = FastAPI(title="Chatbot API", lifespan=lifespan)
register_middleware(app)
register_error_handlers(app)
app.include_router(router)

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/ui", include_in_schema=False)
def chat_page():
    return FileResponse(STATIC_DIR / "index.html")