"""Configuration for the Hex API SDK."""

import os
from typing import Any


class HexConfig:
    """Configuration for the Hex API client."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize configuration.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the Hex API (default: https://app.hex.tech/api)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key: str = api_key.strip()
        self.base_url: str = (base_url or "https://app.hex.tech/api").rstrip("/")
        self.timeout: float = timeout
        self.max_retries: int = max_retries
        self.verify_ssl: bool = verify_ssl

    @classmethod
    def from_env(cls, **overrides: Any) -> "HexConfig":
        """Create config from environment variables with optional overrides."""
        # Get API key from overrides or environment
        api_key = overrides.get("api_key") or os.getenv("HEX_API_KEY")

        # Get base URL from overrides or environment
        base_url = overrides.get("base_url") or os.getenv("HEX_API_BASE_URL")

        # Create config with all values
        return cls(
            api_key=api_key,
            base_url=base_url,
            timeout=overrides.get("timeout", 30.0),
            max_retries=overrides.get("max_retries", 3),
            verify_ssl=overrides.get("verify_ssl", True),
        )
