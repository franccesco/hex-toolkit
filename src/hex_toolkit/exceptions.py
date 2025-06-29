"""Exceptions for the Hex API SDK."""

from typing import Any


class HexAPIError(Exception):
    """Base exception for all Hex API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        trace_id: str | None = None,
    ):
        """Initialize the Hex API error.

        Args:
            message: The error message.
            status_code: HTTP status code if applicable.
            response_data: Response data from the API.
            trace_id: Trace ID for debugging.

        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.trace_id = trace_id

    def __str__(self):
        """Return string representation of the error.

        Returns:
            str: Formatted error message with status code and trace ID if available.

        """
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
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        trace_id: str | None = None,
        invalid_params: list[dict[str, Any]] | None = None,
        not_found_params: list[dict[str, Any]] | None = None,
    ):
        """Initialize the validation error.

        Args:
            message: The error message.
            status_code: HTTP status code if applicable.
            response_data: Response data from the API.
            trace_id: Trace ID for debugging.
            invalid_params: List of invalid parameters.
            not_found_params: List of not found parameters.

        """
        super().__init__(message, status_code, response_data, trace_id)
        self.invalid_params = invalid_params or []
        self.not_found_params = not_found_params or []


class HexRateLimitError(HexAPIError):
    """Raised when rate limits are exceeded (429 errors)."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        trace_id: str | None = None,
        retry_after: int | None = None,
    ):
        """Initialize the rate limit error.

        Args:
            message: The error message.
            status_code: HTTP status code if applicable.
            response_data: Response data from the API.
            trace_id: Trace ID for debugging.
            retry_after: Seconds to wait before retrying.

        """
        super().__init__(message, status_code, response_data, trace_id)
        self.retry_after = retry_after


class HexServerError(HexAPIError):
    """Raised when server errors occur (5xx errors)."""

    pass
