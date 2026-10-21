from pathlib import Path

import chatbot.routes as routes_module
from chatbot.routes import router

FORBIDDEN = ["os.getenv", "os.environ", "genai", "make_client", "chatbot.config"]


def test_router_has_the_api_routes():
    paths = {route.path for route in router.routes}
    assert {"/chat", "/history/{session_id}"} <= paths


def test_router_does_not_read_env_or_build_the_provider_client():
    source = Path(routes_module.__file__).read_text()
    for forbidden in FORBIDDEN:
        assert forbidden not in source, f"routes.py must not use {forbidden}"