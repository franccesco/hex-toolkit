"""Tests for run-related CLI commands."""

from unittest.mock import Mock

from hex_toolkit.cli import app
from hex_toolkit.exceptions import HexAPIError
from hex_toolkit.models.runs import RunStatus


class TestRunsStatus:
    """Test 'hex runs status' command."""

    def test_status_basic(self, runner, mock_env_api_key, mock_hex_client, sample_run_status):  # noqa: ARG002
        """Test basic run status retrieval."""
        mock_hex_client.runs.get_status.return_value = sample_run_status

        result = runner.invoke(app, ["runs", "status", "project-123", "run-456"])

        assert result.exit_code == 0
        assert "Run Status" in result.output
        assert sample_run_status.run_id in result.output
        assert "COMPLETED" in result.output

        mock_hex_client.runs.get_status.assert_called_once_with("project-123", "run-456")

    def test_status_running(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test status display for running job."""
        status = Mock(
            run_id="run-123",
            project_id="project-123",
            status="RUNNING",
            start_time=Mock(),
            end_time=None,
        )
        mock_hex_client.runs.get_status.return_value = status

        result = runner.invoke(app, ["runs", "status", "project-123", "run-123"])

        assert result.exit_code == 0
        assert "RUNNING" in result.output
        assert "N/A" in result.output  # End time should be N/A

    def test_status_not_found(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test handling of run not found."""
        mock_hex_client.runs.get_status.side_effect = HexAPIError(
            "Run not found", status_code=404
        )

        result = runner.invoke(app, ["runs", "status", "project-123", "invalid-run"])

        assert result.exit_code == 1
        assert "Run not found" in result.output

    def test_status_api_error(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test handling of API errors."""
        mock_hex_client.runs.get_status.side_effect = HexAPIError(
            "Internal server error", status_code=500, trace_id="test-trace"
        )

        result = runner.invoke(app, ["runs", "status", "project-123", "run-456"])

        assert result.exit_code == 1
        assert "Internal server error" in result.output


class TestRunsList:
    """Test 'hex runs list' command."""

    def test_list_basic(self, runner, mock_env_api_key, mock_hex_client, sample_runs):  # noqa: ARG002
        """Test basic run listing."""
        mock_hex_client.runs.list.return_value = Mock(runs=sample_runs)

        result = runner.invoke(app, ["runs", "list", "project-123"])

        assert result.exit_code == 0
        assert "Runs for Project project-123" in result.output
        assert "run-0" in result.output
        assert "run-1" in result.output
        assert "COMPLETED" in result.output
        assert "RUNNING" in result.output
        assert "FAILED" in result.output

        mock_hex_client.runs.list.assert_called_once_with(
            "project-123",
            limit=10,
            offset=0,
            status_filter=None,
        )

    def test_list_with_options(self, runner, mock_env_api_key, mock_hex_client, sample_runs):  # noqa: ARG002
        """Test run listing with options."""
        mock_hex_client.runs.list.return_value = Mock(runs=sample_runs[:2])

        result = runner.invoke(app, [
            "runs", "list", "project-123",
            "--limit", "20",
            "--offset", "5",
        ])

        assert result.exit_code == 0
        mock_hex_client.runs.list.assert_called_once_with(
            "project-123",
            limit=20,
            offset=5,
            status_filter=None,
        )

    def test_list_with_status_filter(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test run listing with status filter."""
        from datetime import datetime

        completed_runs = [Mock(
            run_id="run-1",
            status="COMPLETED",
            start_time=datetime(2024, 1, 1, 10, 0, 0),
            end_time=datetime(2024, 1, 1, 10, 5, 0),
        )]
        mock_hex_client.runs.list.return_value = Mock(runs=completed_runs)

        result = runner.invoke(app, [
            "runs", "list", "project-123",
            "--status", "completed",
        ])

        assert result.exit_code == 0
        mock_hex_client.runs.list.assert_called_once()
        # Check that RunStatus enum was used
        assert mock_hex_client.runs.list.call_args[1]["status_filter"] == RunStatus.COMPLETED

    def test_list_invalid_status_filter(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test error with invalid status filter."""
        result = runner.invoke(app, [
            "runs", "list", "project-123",
            "--status", "invalid-status",
        ])

        assert result.exit_code == 1
        assert "Invalid status: invalid-status" in result.output
        assert "Valid options:" in result.output

    def test_list_empty_results(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test listing with no runs."""
        mock_hex_client.runs.list.return_value = Mock(runs=[])

        result = runner.invoke(app, ["runs", "list", "project-123"])

        assert result.exit_code == 0
        assert "No runs found" in result.output

    def test_list_duration_calculation(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test duration calculation in run list."""
        from datetime import datetime

        runs = [
            Mock(
                run_id="short-run",
                status="COMPLETED",
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 30),  # 30 seconds
            ),
            Mock(
                run_id="medium-run",
                status="COMPLETED",
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 5, 0),  # 5 minutes
            ),
            Mock(
                run_id="long-run",
                status="COMPLETED",
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 12, 30, 0),  # 2.5 hours
            ),
        ]
        mock_hex_client.runs.list.return_value = Mock(runs=runs)

        result = runner.invoke(app, ["runs", "list", "project-123"])

        assert result.exit_code == 0
        assert "30s" in result.output  # Short run
        assert "5m" in result.output   # Medium run
        assert "2h 30m" in result.output  # Long run

    def test_list_shows_count(self, runner, mock_env_api_key, mock_hex_client, sample_runs):  # noqa: ARG002
        """Test run count is displayed."""
        mock_hex_client.runs.list.return_value = Mock(runs=sample_runs)

        result = runner.invoke(app, ["runs", "list", "project-123"])

        assert result.exit_code == 0
        assert f"Showing {len(sample_runs)} runs" in result.output


class TestRunsCancel:
    """Test 'hex runs cancel' command."""

    def test_cancel_with_confirmation(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test cancel with user confirmation."""
        mock_hex_client.runs.cancel.return_value = None

        # Simulate user confirming
        result = runner.invoke(app, ["runs", "cancel", "project-123", "run-456"], input="y\n")

        assert result.exit_code == 0
        assert "Are you sure you want to cancel run run-456?" in result.output
        assert "Run run-456 cancelled successfully" in result.output
        mock_hex_client.runs.cancel.assert_called_once_with("project-123", "run-456")

    def test_cancel_declined(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test cancel declined by user."""
        # Simulate user declining
        result = runner.invoke(app, ["runs", "cancel", "project-123", "run-456"], input="n\n")

        assert result.exit_code == 0
        assert "Are you sure you want to cancel run run-456?" in result.output
        assert "Cancelled" in result.output
        mock_hex_client.runs.cancel.assert_not_called()

    def test_cancel_with_yes_flag(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test cancel with --yes flag skips confirmation."""
        mock_hex_client.runs.cancel.return_value = None

        result = runner.invoke(app, ["runs", "cancel", "project-123", "run-456", "--yes"])

        assert result.exit_code == 0
        assert "Are you sure" not in result.output  # No confirmation prompt
        assert "Run run-456 cancelled successfully" in result.output
        mock_hex_client.runs.cancel.assert_called_once_with("project-123", "run-456")

    def test_cancel_not_found(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test handling of run not found during cancel."""
        mock_hex_client.runs.cancel.side_effect = HexAPIError(
            "Run not found", status_code=404
        )

        result = runner.invoke(app, ["runs", "cancel", "project-123", "invalid-run", "--yes"])

        assert result.exit_code == 1
        assert "Run not found" in result.output

    def test_cancel_already_completed(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test cancelling an already completed run."""
        mock_hex_client.runs.cancel.side_effect = HexAPIError(
            "Cannot cancel completed run", status_code=400
        )

        result = runner.invoke(app, ["runs", "cancel", "project-123", "completed-run", "--yes"])

        assert result.exit_code == 1
        assert "Cannot cancel completed run" in result.output

    def test_cancel_general_error(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test handling of general errors during cancel."""
        mock_hex_client.runs.cancel.side_effect = Exception("Network error")

        result = runner.invoke(app, ["runs", "cancel", "project-123", "run-456", "--yes"])

        assert result.exit_code == 1
        assert "Network error" in result.output
