"""Tests for the projects resource."""

from unittest.mock import Mock
from uuid import UUID

from hex_toolkit.client import HexClient
from hex_toolkit.models.projects import Project, ProjectList
from hex_toolkit.models.runs import ProjectRunResponse


class TestProjectsResource:
    """Test ProjectsResource methods."""

    def test_get_project(
        self, hex_client: HexClient, mock_response: Mock, sample_project_data: dict
    ):
        """Test getting a single project."""
        mock_response.json.return_value = sample_project_data
        hex_client._client.request.return_value = mock_response

        project = hex_client.projects.get("12345678-1234-1234-1234-123456789012")

        assert isinstance(project, Project)
        assert project.id == UUID("12345678-1234-1234-1234-123456789012")
        assert project.title == "Test Project"
        assert project.type == "PROJECT"

        hex_client._client.request.assert_called_once_with(
            "GET",
            "/v1/projects/12345678-1234-1234-1234-123456789012",
            params={"includeSharing": False},
        )

    def test_get_project_with_sharing(
        self, hex_client: HexClient, mock_response: Mock, sample_project_data: dict
    ):
        """Test getting a project with sharing information."""
        sample_project_data["sharing"] = {
            "users": [],
            "collections": [],
            "groups": [],
            "workspace": {"access": "CAN_VIEW"},
            "publicWeb": {"access": "NONE"},
            "support": {"access": "NONE"},
        }
        mock_response.json.return_value = sample_project_data
        hex_client._client.request.return_value = mock_response

        project = hex_client.projects.get(
            "12345678-1234-1234-1234-123456789012", include_sharing=True
        )

        assert project.sharing is not None
        assert project.sharing.workspace.access == "CAN_VIEW"

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

        result = hex_client.projects.list(limit=10)

        assert isinstance(result, ProjectList)
        assert len(result.values) == 1
        assert result.values[0].id == UUID("12345678-1234-1234-1234-123456789012")
        assert result.pagination.after == "cursor123"

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

        result = hex_client.projects.run(
            "12345678-1234-1234-1234-123456789012",
            input_params={"param1": "value1"},
            dry_run=True,
        )

        assert isinstance(result, ProjectRunResponse)
        assert result.run_id == UUID("87654321-4321-4321-4321-210987654321")
        assert result.run_url == "https://test.hex.tech/app/runs/test-run"

        hex_client._client.request.assert_called_once_with(
            "POST",
            "/v1/projects/12345678-1234-1234-1234-123456789012/runs",
            json={
                "inputParams": {"param1": "value1"},
                "dryRun": True,
                "updatePublishedResults": False,
                "useCachedSqlResults": True,
            },
        )
