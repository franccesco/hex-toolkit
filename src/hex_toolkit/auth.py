"""Authentication handling for the Hex API SDK."""

from collections.abc import Generator

import httpx


class HexAuth(httpx.Auth):
    """Bearer token authentication for Hex API."""

    def __init__(self, api_key: str) -> None:
        """Initialize the bearer token authentication.

        Args:
            api_key: The Hex API key for authentication.

        """
        self.api_key = api_key

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Apply authentication to the request.

        Yields:
            httpx.Request: The authenticated request.

        """
        request.headers["Authorization"] = f"Bearer {self.api_key}"
        yield request

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns:
            dict[str, str]: Dictionary containing the Authorization header.

        """
        return {"Authorization": f"Bearer {self.api_key}"}
