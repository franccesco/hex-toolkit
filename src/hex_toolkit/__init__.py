"""Hex Python Toolkit - A comprehensive toolkit for working with Hex."""

from hex_toolkit.client import HexClient
from hex_toolkit.exceptions import (
    HexAPIError,
    HexAuthenticationError,
    HexNotFoundError,
    HexRateLimitError,
    HexValidationError,
)

# Get version from package metadata
try:
    from importlib.metadata import version

    __version__ = version("hex-toolkit")
except Exception:
    # Fallback for development or when package isn't installed
    __version__ = "0.5.3"
__all__ = [
    "HexClient",
    "HexAPIError",
    "HexAuthenticationError",
    "HexNotFoundError",
    "HexRateLimitError",
    "HexValidationError",
]
