"""Tests for the Hex client."""

import os
from unittest.mock import Mock, patch

import httpx
import pytest

from hex_toolkit import HexClient
from hex_toolkit.config import HexConfig
from hex_toolkit.exceptions import (
    HexAuthenticationError,
    HexNotFoundError,
    HexRateLimitError,
    HexServerError,
    HexValidationError,
)


class TestHexConfig:
    """Test HexConfig class."""

    def test_config_from_env(self):
        """Test creating config from environment variables."""
        with patch.dict(
            os.environ,
            {
                "HEX_API_KEY": "env-api-key",
                "HEX_API_BASE_URL": "https://env.hex.tech/api",
            },
        ):
            config = HexConfig.from_env()
            assert config.api_key == "env-api-key"
            assert config.base_url == "https://env.hex.tech/api"
            assert config.timeout == 30.0
            assert config.max_retries == 3

    def test_config_with_overrides(self):
        """Test config with overrides."""
        config = HexConfig.from_env(
            api_key="override-key",
            timeout=60.0,
        )
        assert config.api_key == "override-key"
        assert config.timeout == 60.0

    def test_config_validation(self):
        """Test config validation."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            HexConfig(api_key="")

        # Empty string base_url should use default
        config = HexConfig(api_key="test", base_url="")
        assert config.base_url == "https://app.hex.tech/api"


class TestHexClient:
    """Test HexClient class."""

    def test_client_initialization(self, test_config: HexConfig):
        """Test client initialization."""
        with patch("httpx.Client") as mock_client:
            client = HexClient(config=test_config)

            mock_client.assert_called_once()
            assert client.config == test_config
            assert hasattr(client, "projects")
            assert hasattr(client, "runs")
            assert hasattr(client, "embedding")
            assert hasattr(client, "semantic_models")

    def test_client_from_api_key(self):
        """Test creating client from API key."""
        with patch("httpx.Client"):
            client = HexClient(api_key="test-key")
            assert client.config.api_key == "test-key"

    def test_client_context_manager(self, hex_client: HexClient):
        """Test client as context manager."""
        with hex_client as client:
            assert client == hex_client

        hex_client._client.close.assert_called_once()

    def test_request_success(self, hex_client: HexClient, mock_response: Mock):
        """Test successful request."""
        hex_client._client.request.return_value = mock_response

        response = hex_client.request("GET", "/test")

        assert response == mock_response
        hex_client._client.request.assert_called_once_with("GET", "/test")

    def test_request_authentication_error(self, hex_client: HexClient):
        """Test authentication error handling."""
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 401
        error_response.json.return_value = {
            "reason": "Unauthorized",
            "traceId": "test-trace",
        }
        hex_client._client.request.return_value = error_response

        with pytest.raises(HexAuthenticationError) as exc_info:
            hex_client.request("GET", "/test")

        assert "Authentication failed" in str(exc_info.value)
        assert exc_info.value.status_code == 401
        assert exc_info.value.trace_id == "test-trace"

    def test_request_not_found_error(self, hex_client: HexClient):
        """Test not found error handling."""
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 404
        error_response.json.return_value = {"reason": "Not found"}
        hex_client._client.request.return_value = error_response

        with pytest.raises(HexNotFoundError) as exc_info:
            hex_client.request("GET", "/test")

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    def test_request_validation_error(self, hex_client: HexClient):
        """Test validation error handling."""
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 422
        error_response.json.return_value = {
            "reason": "Validation failed",
            "invalid": [{"paramName": "test"}],
            "notFound": ["param1"],
        }
        hex_client._client.request.return_value = error_response

        with pytest.raises(HexValidationError) as exc_info:
            hex_client.request("POST", "/test")

        assert "Validation error" in str(exc_info.value)
        assert exc_info.value.status_code == 422
        assert len(exc_info.value.invalid_params) == 1
        assert exc_info.value.not_found_params == ["param1"]

    def test_request_rate_limit_error(self, hex_client: HexClient):
        """Test rate limit error handling."""
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 429
        error_response.json.return_value = {"reason": "Rate limit exceeded"}
        error_response.headers = {"Retry-After": "60"}
        hex_client._client.request.return_value = error_response

        with pytest.raises(HexRateLimitError) as exc_info:
            hex_client.request("GET", "/test")

        assert "Rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_request_server_error(self, hex_client: HexClient):
        """Test server error handling."""
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 500
        error_response.json.return_value = {"reason": "Internal error"}
        hex_client._client.request.return_value = error_response

        with pytest.raises(HexServerError) as exc_info:
            hex_client.request("GET", "/test")

        assert "Server error" in str(exc_info.value)
        assert exc_info.value.status_code == 500
