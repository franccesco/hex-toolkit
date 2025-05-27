"""Optional integration tests for the Hex API SDK.

These tests make real API calls and require a valid API key.
Run with: HEX_API_KEY=xxx pytest tests/test_integration.py -v

To skip these tests during normal test runs, they are marked with @pytest.mark.integration
"""

import os

import pytest

from hex_api import HexClient
from hex_api.exceptions import HexAPIError


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("HEX_API_KEY"), reason="No API key provided")
class TestIntegration:
    """Integration tests that use the real Hex API."""

    @pytest.fixture
    def client(self):
        """Create a real HexClient instance."""
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
            assert hasattr(result, "values")
            assert hasattr(result, "pagination")
            assert isinstance(result.values, list)
            assert len(result.values) <= 1

            # If we got a project, verify it has expected fields
            if result.values:
                project = result.values[0]
                assert hasattr(project, "id")
                assert hasattr(project, "title")
                assert hasattr(project, "type")

        except HexAPIError as e:
            # If we get a 403, it might mean the API key is valid but doesn't have permissions
            if hasattr(e, "status_code") and e.status_code == 403:
                pytest.skip(f"API key lacks permissions: {e}")
            raise

    def test_get_project_by_id(self, client):
        """Test fetching a specific project if we have permissions."""
        # First, try to get any project
        result = client.projects.list(limit=1)

        if not result.values:
            pytest.skip("No projects available to test with")

        project_id = result.values[0].id

        # Now fetch that specific project
        project = client.projects.get(project_id)

        assert project.id == project_id
        assert hasattr(project, "title")
        assert hasattr(project, "status")
        assert hasattr(project, "type")

    def test_error_handling_invalid_project(self, client):
        """Test that proper errors are raised for invalid project IDs."""
        with pytest.raises(HexAPIError) as exc_info:
            client.projects.get("invalid-project-id-that-does-not-exist")

        # Should get a 404 or similar error
        assert hasattr(exc_info.value, "message")


# Add a simple check that can be run without pytest
if __name__ == "__main__":
    if not os.getenv("HEX_API_KEY"):
        print("Please set HEX_API_KEY environment variable to run integration tests")
        exit(1)

    print("Running manual integration test...")
    client = HexClient()

    try:
        result = client.projects.list(limit=1)
        print("✓ Successfully connected to Hex API")
        projects = result.values
        print(f"✓ Found {len(projects)} project(s)")
        if projects:
            print(f"✓ First project: {projects[0].title}")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        exit(1)
