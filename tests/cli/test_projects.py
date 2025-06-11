"""Tests for project-related CLI commands."""

import json
from datetime import datetime
from unittest.mock import Mock, patch

from hex_toolkit.cli import app
from hex_toolkit.exceptions import HexAPIError
from hex_toolkit.models.projects import SortBy, SortDirection


class TestProjectsList:
    """Test 'hex projects list' command."""

    def test_list_basic(self, runner, mock_env_api_key, mock_hex_client, mock_list_response):  # noqa: ARG002
        """Test basic project listing."""
        mock_hex_client.projects.list.return_value = mock_list_response

        result = runner.invoke(app, ["projects", "list"])

        assert result.exit_code == 0
        assert "Hex Projects" in result.output
        assert "Project 0" in result.output
        assert "Project 1" in result.output
        assert "Project 2" in result.output

        # Verify API was called with defaults
        mock_hex_client.projects.list.assert_called_once_with(
            limit=25,
            include_archived=False,
            include_trashed=False,
            creator_email=None,
            owner_email=None,
            sort_by=None,
            sort_direction=None,
        )

    def test_list_with_limit(self, runner, mock_env_api_key, mock_hex_client, mock_list_response):  # noqa: ARG002
        """Test listing with custom limit."""
        mock_hex_client.projects.list.return_value = mock_list_response

        result = runner.invoke(app, ["projects", "list", "--limit", "50"])

        assert result.exit_code == 0
        mock_hex_client.projects.list.assert_called_once()
        assert mock_hex_client.projects.list.call_args[1]["limit"] == 50

    def test_list_with_filters(self, runner, mock_env_api_key, mock_hex_client, mock_list_response):  # noqa: ARG002
        """Test listing with various filters."""
        mock_hex_client.projects.list.return_value = mock_list_response

        result = runner.invoke(app, [
            "projects", "list",
            "--include-archived",
            "--include-trashed",
            "--creator-email", "creator@test.com",
            "--owner-email", "owner@test.com",
        ])

        assert result.exit_code == 0
        mock_hex_client.projects.list.assert_called_once_with(
            limit=25,
            include_archived=True,
            include_trashed=True,
            creator_email="creator@test.com",
            owner_email="owner@test.com",
            sort_by=None,
            sort_direction=None,
        )

    def test_list_with_sort_ascending(self, runner, mock_env_api_key, mock_hex_client, mock_list_response):  # noqa: ARG002
        """Test listing with ascending sort."""
        mock_hex_client.projects.list.return_value = mock_list_response

        result = runner.invoke(app, ["projects", "list", "--sort", "created_at"])

        assert result.exit_code == 0
        mock_hex_client.projects.list.assert_called_once()
        assert mock_hex_client.projects.list.call_args[1]["sort_by"] == SortBy.CREATED_AT
        assert mock_hex_client.projects.list.call_args[1]["sort_direction"] == SortDirection.ASC

    def test_list_with_sort_descending(self, runner, mock_env_api_key, mock_hex_client, mock_list_response):  # noqa: ARG002
        """Test listing with descending sort."""
        mock_hex_client.projects.list.return_value = mock_list_response

        result = runner.invoke(app, ["projects", "list", "--sort", "-last_edited_at"])

        assert result.exit_code == 0
        mock_hex_client.projects.list.assert_called_once()
        assert mock_hex_client.projects.list.call_args[1]["sort_by"] == SortBy.LAST_EDITED_AT
        assert mock_hex_client.projects.list.call_args[1]["sort_direction"] == SortDirection.DESC

    def test_list_invalid_sort_field(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test error with invalid sort field."""
        result = runner.invoke(app, ["projects", "list", "--sort", "invalid_field"])

        assert result.exit_code == 1
        assert "Invalid sort field 'invalid_field'" in result.output

    def test_list_custom_columns(self, runner, mock_env_api_key, mock_hex_client, mock_list_response):  # noqa: ARG002
        """Test listing with custom columns."""
        mock_hex_client.projects.list.return_value = mock_list_response

        result = runner.invoke(app, [
            "projects", "list",
            "--columns", "id,name,creator,last_viewed_at,app_views"
        ])

        assert result.exit_code == 0
        # Table should include custom columns
        assert "Creator" in result.output
        assert "Last Viewed At" in result.output
        assert "App Views" in result.output

    def test_list_empty_results(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test listing with no projects."""
        mock_hex_client.projects.list.return_value = Mock(values=[], pagination=None)

        result = runner.invoke(app, ["projects", "list"])

        assert result.exit_code == 0
        assert "No projects found" in result.output

    def test_list_with_pagination_hint(self, runner, mock_env_api_key, mock_hex_client, mock_list_response):  # noqa: ARG002
        """Test pagination hint is shown."""
        mock_list_response.pagination.after = "next-cursor"
        mock_hex_client.projects.list.return_value = mock_list_response

        result = runner.invoke(app, ["projects", "list"])

        assert result.exit_code == 0
        assert "More results available" in result.output

    def test_list_api_error(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test handling of API errors."""
        mock_hex_client.projects.list.side_effect = HexAPIError(
            "API Error", status_code=500, trace_id="test-trace"
        )

        result = runner.invoke(app, ["projects", "list"])

        assert result.exit_code == 1
        assert "API Error" in result.output

    def test_list_with_search(self, runner, mock_env_api_key, mock_hex_client, sample_projects):  # noqa: ARG002
        """Test project search functionality."""
        # Mock paginated responses
        mock_hex_client.projects.list.side_effect = [
            Mock(values=sample_projects[:2], pagination=Mock(after="cursor1")),
            Mock(values=[sample_projects[2]], pagination=Mock(after=None)),
        ]

        result = runner.invoke(app, ["projects", "list", "--search", "Project 1"])

        assert result.exit_code == 0
        assert "Project 1" in result.output
        assert "Found 1 project(s) matching 'Project 1'" in result.output
        # Should have called list multiple times for pagination
        assert mock_hex_client.projects.list.call_count == 2


class TestProjectsGet:
    """Test 'hex projects get' command."""

    def test_get_basic(self, runner, mock_env_api_key, mock_hex_client, sample_project):  # noqa: ARG002
        """Test basic project retrieval."""
        mock_hex_client.projects.get.return_value = sample_project

        result = runner.invoke(app, ["projects", "get", "project-123"])

        assert result.exit_code == 0
        assert "Test Project" in result.output
        assert "Basic Information" in result.output
        assert "People" in result.output
        assert "Timestamps" in result.output

        mock_hex_client.projects.get.assert_called_once_with(
            "project-123", include_sharing=False
        )

    def test_get_with_sharing(self, runner, mock_env_api_key, mock_hex_client, sample_project):  # noqa: ARG002
        """Test project retrieval with sharing info."""
        mock_hex_client.projects.get.return_value = sample_project

        result = runner.invoke(app, ["projects", "get", "project-123", "--include-sharing"])
        assert result.exit_code == 0
        assert "Sharing & Permissions" in result.output
        assert "Workspace" in result.output

        mock_hex_client.projects.get.assert_called_once_with(
            "project-123", include_sharing=True
        )

    def test_get_project_not_found(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test handling of project not found."""
        mock_hex_client.projects.get.side_effect = HexAPIError(
            "Project not found", status_code=404
        )

        result = runner.invoke(app, ["projects", "get", "invalid-id"])

        assert result.exit_code == 1
        assert "Project not found" in result.output

    def test_get_displays_all_sections(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test all project sections are displayed."""
        # Create a project with all optional fields
        project = Mock(
            id="12345678-1234-1234-1234-123456789012",
            title="Full Project",
            description="A complete project",
            type="PROJECT",
            status=Mock(name="Published"),
            creator=Mock(email="creator@test.com"),
            owner=Mock(email="owner@test.com"),
            created_at=datetime.now(),
            last_edited_at=datetime.now(),
            last_published_at=datetime.now(),
            archived_at=None,
            trashed_at=None,
            analytics=Mock(
                last_viewed_at=datetime.now(),
                published_results_updated_at=datetime.now(),
                app_views=Mock(all_time=1000, last_thirty_days=100, last_seven_days=25)
            ),
            categories=[Mock(name="Category1", description="Desc1")],
            reviews=Mock(required=True),
            schedules=[
                Mock(
                    enabled=True,
                    cadence=Mock(value="DAILY"),
                    daily=Mock(hour=10, minute=30, timezone="UTC")
                )
            ],
            sharing=Mock(
                workspace=Mock(access=Mock(value="CAN_VIEW")),
                public_web=Mock(access=Mock(value="NONE")),
                support=Mock(access=Mock(value="NONE")),
                users=[Mock(user=Mock(email="user@test.com"), access=Mock(value="CAN_EDIT"))],
                groups=[],
                collections=[]
            )
        )

        mock_hex_client.projects.get.return_value = project

        result = runner.invoke(app, ["projects", "get", "test-id", "--include-sharing"])

        assert result.exit_code == 0
        # Verify all sections appear
        assert "Basic Information" in result.output
        assert "People" in result.output
        assert "Timestamps" in result.output
        assert "Analytics" in result.output
        assert "Categories" in result.output
        assert "Reviews" in result.output
        assert "Schedules" in result.output
        assert "Sharing & Permissions" in result.output


class TestProjectsRun:
    """Test 'hex projects run' command."""

    def test_run_basic(self, runner, mock_env_api_key, mock_hex_client, sample_run_info):  # noqa: ARG002
        """Test basic project run."""
        mock_hex_client.projects.run.return_value = sample_run_info

        result = runner.invoke(app, ["projects", "run", "project-123"])

        assert result.exit_code == 0
        assert "Run started successfully" in result.output
        assert sample_run_info.run_id in result.output

        mock_hex_client.projects.run.assert_called_once_with(
            "project-123",
            input_params=None,
            dry_run=False,
            update_published_results=False,
            use_cached_sql_results=True,
        )

    def test_run_with_options(self, runner, mock_env_api_key, mock_hex_client, sample_run_info):  # noqa: ARG002
        """Test project run with various options."""
        mock_hex_client.projects.run.return_value = sample_run_info

        result = runner.invoke(app, [
            "projects", "run", "project-123",
            "--dry-run",
            "--update-cache",
            "--no-sql-cache",
        ])

        assert result.exit_code == 0
        mock_hex_client.projects.run.assert_called_once_with(
            "project-123",
            input_params=None,
            dry_run=True,
            update_published_results=True,
            use_cached_sql_results=False,
        )

    def test_run_with_input_params(self, runner, mock_env_api_key, mock_hex_client, sample_run_info):  # noqa: ARG002
        """Test project run with input parameters."""
        mock_hex_client.projects.run.return_value = sample_run_info
        params = {"key": "value", "number": 42}

        result = runner.invoke(app, [
            "projects", "run", "project-123",
            "--input-params", json.dumps(params),
        ])

        assert result.exit_code == 0
        mock_hex_client.projects.run.assert_called_once()
        assert mock_hex_client.projects.run.call_args[1]["input_params"] == params

    def test_run_invalid_json_params(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test error with invalid JSON parameters."""
        result = runner.invoke(app, [
            "projects", "run", "project-123",
            "--input-params", "invalid json",
        ])

        assert result.exit_code == 1
        assert "Invalid JSON for input parameters" in result.output

    def test_run_with_wait(self, runner, mock_env_api_key, mock_hex_client, sample_run_info):  # noqa: ARG002
        """Test project run with --wait flag."""
        mock_hex_client.projects.run.return_value = sample_run_info

        # Mock status progression
        mock_hex_client.runs.get_status.side_effect = [
            Mock(status="RUNNING"),
            Mock(status="RUNNING"),
            Mock(status="COMPLETED"),
        ]

        with patch("time.sleep"):  # Don't actually sleep in tests
            result = runner.invoke(app, [
                "projects", "run", "project-123",
                "--wait",
                "--poll-interval", "1",
            ])

        assert result.exit_code == 0
        assert "Waiting for run to complete" in result.output
        assert "Run completed with status" in result.output
        assert mock_hex_client.runs.get_status.call_count == 3

    def test_run_wait_keyboard_interrupt(self, runner, mock_env_api_key, mock_hex_client, sample_run_info):  # noqa: ARG002
        """Test interrupting wait with keyboard interrupt."""
        mock_hex_client.projects.run.return_value = sample_run_info
        mock_hex_client.runs.get_status.side_effect = KeyboardInterrupt()

        result = runner.invoke(app, [
            "projects", "run", "project-123",
            "--wait",
        ])

        assert result.exit_code == 0
        assert "Polling cancelled by user" in result.output
