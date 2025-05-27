"""Exceptions for the Hex API SDK."""


class HexAPIError(Exception):
    """Base exception for all Hex API errors."""

    def __init__(
        self,
        message,
        status_code=None,
        response_data=None,
        trace_id=None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.trace_id = trace_id

    def __str__(self):
        parts = [self.message]
        if self.status_code:
            parts.append(f"(Status: {self.status_code})")
        if self.trace_id:
            parts.append(f"(Trace ID: {self.trace_id})")
        return " ".join(parts)


class HexAuthenticationError(HexAPIError):
    """Raised when authentication fails (401/403 errors)."""

    pass


class HexNotFoundError(HexAPIError):
    """Raised when a resource is not found (404 errors)."""

    pass


class HexValidationError(HexAPIError):
    """Raised when request validation fails (400/422 errors)."""

    def __init__(
        self,
        message,
        status_code=None,
        response_data=None,
        trace_id=None,
        invalid_params=None,
        not_found_params=None,
    ):
        super().__init__(message, status_code, response_data, trace_id)
        self.invalid_params = invalid_params or []
        self.not_found_params = not_found_params or []


class HexRateLimitError(HexAPIError):
    """Raised when rate limits are exceeded (429 errors)."""

    def __init__(
        self,
        message,
        status_code=None,
        response_data=None,
        trace_id=None,
        retry_after=None,
    ):
        super().__init__(message, status_code, response_data, trace_id)
        self.retry_after = retry_after


class HexServerError(HexAPIError):
    """Raised when server errors occur (5xx errors)."""

    pass
