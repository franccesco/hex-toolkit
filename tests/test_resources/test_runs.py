"""Tests for the runs resource."""

from unittest.mock import Mock

from hex_api.client import HexClient


class TestRunsResource:
    """Test RunsResource methods."""

    def test_get_run_status(self, hex_client: HexClient, mock_response: Mock):
        """Test getting run status."""
        status_data = {
            "projectId": "12345678-1234-1234-1234-123456789012",
            "runId": "87654321-4321-4321-4321-210987654321",
            "status": "COMPLETED",
            "startTime": "2024-01-01T00:00:00Z",
            "endTime": "2024-01-01T00:01:00Z",
            "elapsedTime": 60000,
        }
        mock_response.json.return_value = status_data
        hex_client._client.request.return_value = mock_response

        result = hex_client.runs.get_status(
            "12345678-1234-1234-1234-123456789012",
            "87654321-4321-4321-4321-210987654321",
        )

        assert isinstance(result, dict)
        assert result["status"] == "COMPLETED"
        assert result["elapsedTime"] == 60000

        hex_client._client.request.assert_called_once_with(
            "GET",
            "/v1/projects/12345678-1234-1234-1234-123456789012/runs/87654321-4321-4321-4321-210987654321",
        )

    def test_list_runs(self, hex_client: HexClient, mock_response: Mock):
        """Test listing runs."""
        runs_data = {
            "runs": [
                {
                    "runId": "run-1",
                    "status": "COMPLETED",
                    "startTime": "2024-01-01T00:00:00Z",
                },
                {
                    "runId": "run-2",
                    "status": "RUNNING",
                    "startTime": "2024-01-01T00:05:00Z",
                },
            ],
            "nextPage": "cursor123",
        }
        mock_response.json.return_value = runs_data
        hex_client._client.request.return_value = mock_response

        result = hex_client.runs.list(
            "12345678-1234-1234-1234-123456789012",
            limit=10,
            status_filter="COMPLETED",
        )

        assert isinstance(result, dict)
        assert "runs" in result
        assert len(result["runs"]) == 2
        assert result["runs"][0]["status"] == "COMPLETED"
        assert result["nextPage"] == "cursor123"

        hex_client._client.request.assert_called_once_with(
            "GET",
            "/v1/projects/12345678-1234-1234-1234-123456789012/runs",
            params={"limit": 10, "statusFilter": "COMPLETED"},
        )

    def test_cancel_run(self, hex_client: HexClient, mock_response: Mock):
        """Test canceling a run."""
        mock_response.json.return_value = {"success": True}
        hex_client._client.request.return_value = mock_response

        result = hex_client.runs.cancel(
            "12345678-1234-1234-1234-123456789012",
            "87654321-4321-4321-4321-210987654321",
        )

        assert result == {"success": True}

        hex_client._client.request.assert_called_once_with(
            "DELETE",
            "/v1/projects/12345678-1234-1234-1234-123456789012/runs/87654321-4321-4321-4321-210987654321",
        )
