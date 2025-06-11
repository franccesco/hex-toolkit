"""Main client for the Hex API SDK."""

from typing import Any

import httpx

from hex_toolkit.auth import HexAuth
from hex_toolkit.config import HexConfig
from hex_toolkit.exceptions import (
    HexAPIError,
    HexAuthenticationError,
    HexNotFoundError,
    HexRateLimitError,
    HexServerError,
    HexValidationError,
)
from hex_toolkit.resources.embedding import EmbeddingResource
from hex_toolkit.resources.projects import ProjectsResource
from hex_toolkit.resources.runs import RunsResource
from hex_toolkit.resources.semantic_models import SemanticModelsResource


class HexClient:
    """Client for the Hex API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        config: HexConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Hex client.

        Args:
            api_key: API key for authentication. Can also be set via HEX_API_KEY env var.
            base_url: Base URL for the API. Defaults to https://app.hex.tech/api
            config: Full configuration object. If provided, other params are ignored.
            **kwargs: Additional configuration options (timeout, max_retries, etc.)
        """
        if config:
            self.config = config
        else:
            self.config = HexConfig.from_env(
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )

        self.auth = HexAuth(self.config.api_key)

        self._client = httpx.Client(
            base_url=self.config.base_url,
            auth=self.auth,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            headers={"User-Agent": "hex-python-sdk/0.1.0"},
        )

        # Initialize resources
        self.projects = ProjectsResource(self)
        self.runs = RunsResource(self)
        self.embedding = EmbeddingResource(self)
        self.semantic_models = SemanticModelsResource(self)

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a request to the API."""
        response = self._client.request(method, path, **kwargs)

        if response.status_code >= 400:
            self._handle_response_error(response)

        return response

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
        except Exception:
            error_data = {}

        trace_id = error_data.get("traceId")
        reason = error_data.get("reason", response.text or "Unknown error")

        if response.status_code == 401:
            raise HexAuthenticationError(
                "Authentication failed. Check your API key.",
                status_code=response.status_code,
                response_data=error_data,
                trace_id=trace_id,
            )
        elif response.status_code == 403:
            raise HexAuthenticationError(
                f"Forbidden: {reason}",
                status_code=response.status_code,
                response_data=error_data,
                trace_id=trace_id,
            )
        elif response.status_code == 404:
            raise HexNotFoundError(
                f"Resource not found: {reason}",
                status_code=response.status_code,
                response_data=error_data,
                trace_id=trace_id,
            )
        elif response.status_code == 422:
            # Handle validation errors with additional details
            invalid_params = error_data.get("invalid", [])
            not_found_params = error_data.get("notFound", [])
            raise HexValidationError(
                f"Validation error: {reason}",
                status_code=response.status_code,
                response_data=error_data,
                trace_id=trace_id,
                invalid_params=invalid_params,
                not_found_params=not_found_params,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise HexRateLimitError(
                f"Rate limit exceeded: {reason}",
                status_code=response.status_code,
                response_data=error_data,
                trace_id=trace_id,
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code >= 500:
            raise HexServerError(
                f"Server error: {reason}",
                status_code=response.status_code,
                response_data=error_data,
                trace_id=trace_id,
            )
        else:
            raise HexAPIError(
                f"API error: {reason}",
                status_code=response.status_code,
                response_data=error_data,
                trace_id=trace_id,
            )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "HexClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
