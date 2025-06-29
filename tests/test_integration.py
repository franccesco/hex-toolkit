"""Optional integration tests for the Hex API SDK.

These tests make real API calls and require a valid API key.
Run with: HEX_API_KEY=xxx pytest tests/test_integration.py -v

To skip these tests during normal test runs, they are marked with @pytest.mark.integration
"""

import os

import pytest

from hex_toolkit import HexClient
from hex_toolkit.exceptions import HexAPIError
from hex_toolkit.models.projects import ProjectList


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("HEX_API_KEY"), reason="No API key provided")
class TestIntegration:
    """Integration tests that use the real Hex API."""

    @pytest.fixture
    def client(self):
        """Create a real HexClient instance.

        Returns:
            HexClient: A real HexClient instance configured with API credentials.

        """
        api_key = os.getenv("HEX_API_KEY")
        base_url = os.getenv("HEX_API_BASE_URL")  # Optional custom base URL

        if base_url:
            return HexClient(api_key=api_key, base_url=base_url)
        return HexClient(api_key=api_key)

    def test_smoke_real_api(self, client):
        """Basic smoke test to verify API connectivity."""
        try:
            # Try to list projects with a small limit
            result = client.projects.list(limit=1)

            # Basic assertions
            assert isinstance(result, ProjectList)
            assert isinstance(result.values, list)
            assert len(result.values) <= 1

            # If we got a project, verify it has expected fields
            if result.values:
                project = result.values[0]
                assert project.id is not None
                assert project.title is not None
                assert project.type is not None

            print(f"✅ API test passed - found {len(result.values)} project(s)")

        except HexAPIError as e:
            pytest.fail(f"API error: {e}")
