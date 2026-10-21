from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from chatbot.error_handlers import register_error_handlers
from chatbot.errors import LLMUnavailableError
from chatbot.middleware import register_middleware


def make_app():
    app = FastAPI()
    register_middleware(app)
    register_error_handlers(app)

    @app.get("/ok")
    def ok(request: Request):
        return {"request_id": request.state.request_id}

    @app.get("/boom")
    def boom():
        raise LLMUnavailableError()

    return app


def test_each_response_has_a_request_id_header():
    response = TestClient(make_app()).get("/ok")
    assert response.headers["x-request-id"]


def test_route_sees_the_same_id_as_the_header():
    response = TestClient(make_app()).get("/ok")
    assert response.json()["request_id"] == response.headers["x-request-id"]


def test_every_request_gets_a_new_id():
    client = TestClient(make_app())
    first = client.get("/ok").headers["x-request-id"]
    second = client.get("/ok").headers["x-request-id"]
    assert first != second


def test_error_body_carries_the_same_request_id():
    response = TestClient(make_app()).get("/boom")
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]