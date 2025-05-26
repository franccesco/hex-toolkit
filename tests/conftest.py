"""Pytest configuration and fixtures."""

from typing import Generator
from unittest.mock import Mock, patch

import httpx
import pytest

from hex_api import HexClient
from hex_api.config import HexConfig


@pytest.fixture
def test_config() -> HexConfig:
    """Create a test configuration."""
    return HexConfig(
        api_key="test-api-key",
        base_url="https://test.hex.tech/api",
        timeout=5.0,
        max_retries=1,
    )


@pytest.fixture
def mock_httpx_client() -> Generator[Mock, None, None]:
    """Mock httpx.Client for testing."""
    with patch("httpx.Client") as mock:
        client_instance = Mock()
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def hex_client(test_config: HexConfig) -> Generator[HexClient, None, None]:
    """Create a HexClient instance for testing."""
    with patch("hex_api.client.httpx.Client") as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        client = HexClient(config=test_config)
        yield client


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock HTTP response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.content = b'{"test": "data"}'
    response.json.return_value = {"test": "data"}
    response.headers = {}
    return response


@pytest.fixture
def mock_error_response() -> Mock:
    """Create a mock error HTTP response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 400
    response.content = b'{"reason": "Bad request", "traceId": "test-trace-id"}'
    response.json.return_value = {
        "reason": "Bad request",
        "traceId": "test-trace-id",
    }
    response.text = "Bad request"
    response.headers = {}
    return response


# Sample data fixtures
@pytest.fixture
def sample_project_data() -> dict:
    """Sample project data for testing."""
    return {
        "id": "12345678-1234-1234-1234-123456789012",
        "title": "Test Project",
        "description": "A test project",
        "type": "PROJECT",
        "creator": {"email": "creator@test.com"},
        "owner": {"email": "owner@test.com"},
        "status": {"name": "active"},
        "categories": [{"name": "Test", "description": "Test category"}],
        "reviews": {"required": False},
        "analytics": {
            "publishedResultsUpdatedAt": "2024-01-01T00:00:00Z",
            "lastViewedAt": "2024-01-01T00:00:00Z",
            "appViews": {
                "lastThirtyDays": 100,
                "lastFourteenDays": 50,
                "lastSevenDays": 25,
                "allTime": 1000,
            },
        },
        "lastEditedAt": "2024-01-01T00:00:00Z",
        "lastPublishedAt": "2024-01-01T00:00:00Z",
        "createdAt": "2024-01-01T00:00:00Z",
        "archivedAt": None,
        "trashedAt": None,
        "schedules": [],
        "sharing": {
            "users": [],
            "collections": [],
            "groups": [],
            "workspace": {"access": "CAN_VIEW"},
            "publicWeb": {"access": "NONE"},
            "support": {"access": "NONE"},
        },
    }


@pytest.fixture
def sample_run_data() -> dict:
    """Sample run data for testing."""
    return {
        "projectId": "12345678-1234-1234-1234-123456789012",
        "runId": "87654321-4321-4321-4321-210987654321",
        "runUrl": "https://test.hex.tech/app/runs/test-run",
        "runStatusUrl": "https://test.hex.tech/api/v1/projects/test/runs/test-run",
        "traceId": "test-trace-id",
        "projectVersion": 42,
        "notifications": [],
    }


@pytest.fixture
def sample_embedding_data() -> dict:
    """Sample embedding data for testing."""
    return {
        "url": "https://test.hex.tech/embed/signed-url",
    }
