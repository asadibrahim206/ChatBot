import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from chatbot.error_handlers import register_error_handlers
from chatbot.errors import (
    AppError,
    LLMConfigurationError,
    LLMRateLimitError,
    LLMUnavailableError,
)


def make_client(error):
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    def boom():
        raise error

    return TestClient(app)


@pytest.mark.parametrize(
    "error, status, code",
    [
        (LLMUnavailableError(), 503, "llm_unavailable"),
        (LLMRateLimitError(), 429, "llm_rate_limited"),
        (LLMConfigurationError(), 500, "llm_misconfigured"),
    ],
)
def test_handler_turns_llm_errors_into_json(error, status, code):
    response = make_client(error).get("/boom")

    assert response.status_code == status
    assert response.json() == {
        "error": {"code": code, "message": error.message, "request_id": None}
    }


def test_handler_covers_any_app_error():
    class TeapotError(AppError):
        status_code = 418
        code = "teapot"
        message = "I am a teapot."

    response = make_client(TeapotError()).get("/boom")

    assert response.status_code == 418
    assert response.json()["error"]["code"] == "teapot"