import pytest

from chatbot.errors import (
    LLMConfigurationError,
    LLMError,
    LLMRateLimitError,
    LLMUnavailableError,
)


@pytest.mark.parametrize(
    "error_class, code, status",
    [
        (LLMUnavailableError, "llm_unavailable", 503),
        (LLMRateLimitError, "llm_rate_limited", 429),
        (LLMConfigurationError, "llm_misconfigured", 500),
    ],
)
def test_error_has_code_and_status(error_class, code, status):
    error = error_class()
    assert error.code == code
    assert error.status_code == status
    assert error.message


def test_llm_errors_share_a_base_class():
    for error_class in (LLMUnavailableError, LLMRateLimitError, LLMConfigurationError):
        assert issubclass(error_class, LLMError)

