from uuid import uuid4

from fastapi import FastAPI, Request

REQUEST_ID_HEADER = "X-Request-ID"


async def add_request_id(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

    response.headers[REQUEST_ID_HEADER] = request_id
    return response


def register_middleware(app: FastAPI) -> None:
    app.middleware("http")(add_request_id)