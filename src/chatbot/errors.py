class AppError(Exception):
    """Base class for errors the API reports to clients in a consistent way."""

    status_code = 500
    code = "internal_error"
    message = "Something went wrong on our side."

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class LLMError(AppError):
    """Base class for failures of the LLM provider."""

    status_code = 502
    code = "llm_error"
    message = "The chatbot service had a problem."


class LLMUnavailableError(LLMError):
    status_code = 503
    code = "llm_unavailable"
    message = "The chatbot service is temporarily unavailable."


class LLMRateLimitError(LLMError):
    status_code = 429
    code = "llm_rate_limited"
    message = "The chatbot service is busy. Please try again shortly."


class LLMConfigurationError(LLMError):
    status_code = 500
    code = "llm_misconfigured"
    message = "The chatbot service is not configured correctly."