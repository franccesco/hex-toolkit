"""Tests for projects resource."""

from unittest.mock import Mock

from hex_api import HexClient
from hex_api.models.projects import Project, ProjectList
from hex_api.models.runs import ProjectRunResponse


class TestProjectsResource:
    """Test ProjectsResource class."""

    def test_get_project(
        self, hex_client: HexClient, mock_response: Mock, sample_project_data: dict
    ):
        """Test getting a single project."""
        mock_response.json.return_value = sample_project_data
        hex_client._client.request.return_value = mock_response

        project = hex_client.projects.get("12345678-1234-1234-1234-123456789012")

        assert isinstance(project, Project)
        assert str(project.id) == "12345678-1234-1234-1234-123456789012"
        assert project.title == "Test Project"

        hex_client._client.request.assert_called_once_with(
            "GET",
            "/v1/projects/12345678-1234-1234-1234-123456789012",
            params={"includeSharing": False},
        )

    def test_get_project_with_sharing(
        self, hex_client: HexClient, mock_response: Mock, sample_project_data: dict
    ):
        """Test getting a project with sharing info."""
        mock_response.json.return_value = sample_project_data
        hex_client._client.request.return_value = mock_response

        project = hex_client.projects.get(
            "12345678-1234-1234-1234-123456789012",
            include_sharing=True,
        )

        hex_client._client.request.assert_called_once_with(
            "GET",
            "/v1/projects/12345678-1234-1234-1234-123456789012",
            params={"includeSharing": True},
        )

    def test_list_projects(
        self, hex_client: HexClient, mock_response: Mock, sample_project_data: dict
    ):
        """Test listing projects."""
        list_data = {
            "values": [sample_project_data],
            "pagination": {"after": "cursor123", "before": None},
        }
        mock_response.json.return_value = list_data
        hex_client._client.request.return_value = mock_response

        project_list = hex_client.projects.list(limit=10)

        assert isinstance(project_list, ProjectList)
        assert len(project_list.values) == 1
        assert project_list.pagination.after == "cursor123"

        hex_client._client.request.assert_called_once()
        call_args = hex_client._client.request.call_args
        assert call_args[0] == ("GET", "/v1/projects")
        assert call_args[1]["params"]["limit"] == 10

    def test_run_project(
        self, hex_client: HexClient, mock_response: Mock, sample_run_data: dict
    ):
        """Test running a project."""
        mock_response.json.return_value = sample_run_data
        hex_client._client.request.return_value = mock_response

        run = hex_client.projects.run(
            "12345678-1234-1234-1234-123456789012",
            input_params={"param1": "value1"},
            dry_run=True,
        )

        assert isinstance(run, ProjectRunResponse)
        assert str(run.run_id) == "87654321-4321-4321-4321-210987654321"
        assert run.project_version == 42

        hex_client._client.request.assert_called_once()
        call_args = hex_client._client.request.call_args
        assert call_args[0] == (
            "POST",
            "/v1/projects/12345678-1234-1234-1234-123456789012/runs",
        )
        assert "json" in call_args[1]
        assert call_args[1]["json"]["inputParams"] == {"param1": "value1"}
        assert call_args[1]["json"]["dryRun"] is True
