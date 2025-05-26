"""Authentication handling for the Hex API SDK."""

from typing import Dict

import httpx


class HexAuth(httpx.Auth):
    """Bearer token authentication for Hex API."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def auth_flow(self, request: httpx.Request):
        """Apply authentication to the request."""
        request.headers["Authorization"] = f"Bearer {self.api_key}"
        yield request

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {"Authorization": f"Bearer {self.api_key}"}