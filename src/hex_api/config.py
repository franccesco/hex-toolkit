"""Configuration for the Hex API SDK."""

import os

from pydantic import BaseModel, Field, field_validator


class HexConfig(BaseModel):
    """Configuration for the Hex API client."""

    api_key: str = Field(..., description="API key for authentication")
    base_url: str = Field(
        default="https://app.hex.tech/api",
        description="Base URL for the Hex API",
    )
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds",
        ge=0.0,
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests",
        ge=0,
    )
    verify_ssl: bool = Field(
        default=True,
        description="Whether to verify SSL certificates",
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v.strip()

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate and clean base URL."""
        v = v.strip()
        if not v:
            raise ValueError("Base URL cannot be empty")
        # Remove trailing slash
        return v.rstrip("/")

    @classmethod
    def from_env(cls, **overrides) -> "HexConfig":
        """Create config from environment variables with optional overrides."""
        config_data = {}

        # Check for API key in environment
        api_key = overrides.get("api_key") or os.getenv("HEX_API_KEY")
        if api_key:
            config_data["api_key"] = api_key

        # Check for base URL in environment
        base_url = overrides.get("base_url") or os.getenv("HEX_API_BASE_URL")
        if base_url:
            config_data["base_url"] = base_url

        # Apply any other overrides
        config_data.update({k: v for k, v in overrides.items() if v is not None})

        return cls(**config_data)
