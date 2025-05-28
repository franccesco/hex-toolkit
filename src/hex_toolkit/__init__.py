"""Hex Python Toolkit - A comprehensive toolkit for working with Hex."""

from hex_toolkit.client import HexClient
from hex_toolkit.exceptions import (
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
