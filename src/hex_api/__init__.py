"""Hex Python SDK - A Python client for the Hex API."""

from hex_api.client import HexClient
from hex_api.exceptions import (
    HexAPIError,
    HexAuthenticationError,
    HexNotFoundError,
    HexRateLimitError,
    HexValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "HexClient",
    "HexAPIError",
    "HexAuthenticationError",
    "HexNotFoundError",
    "HexRateLimitError",
    "HexValidationError",
]
