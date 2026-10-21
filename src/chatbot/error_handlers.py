import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from chatbot.errors import AppError

logger = logging.getLogger(__name__)


def error_body(code: str, message: str, request_id: str | None) -> dict:
    return {"error": {"code": code, "message": message, "request_id": request_id}}


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)

    level = logging.ERROR if exc.status_code >= 500 else logging.WARNING
    logger.log(level, "%s (request_id=%s)", exc.code, request_id, exc_info=exc)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, request_id),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)