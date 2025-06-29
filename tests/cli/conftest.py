"""Shared fixtures for CLI tests."""

from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from typer.testing import CliRunner

from hex_toolkit.models.projects import (
    AccessLevel,
    AnalyticsInfo,
    AppViewsInfo,
    CategoryInfo,
    CreatorInfo,
    Project,
    ProjectType,
    PublicWebAccess,
    ReviewsInfo,
    SharingInfo,
    StatusInfo,
    SupportAccess,
    UserInfo,
    WorkspaceAccess,
)


@pytest.fixture
def runner():
    """Create a CLI runner for testing.

    Returns:
        CliRunner: A Typer CLI test runner instance.

    """
    return CliRunner()


@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Mock HEX_API_KEY environment variable."""
    monkeypatch.setenv("HEX_API_KEY", "test-api-key")


@pytest.fixture
def mock_env_no_api_key(monkeypatch):
    """Remove HEX_API_KEY environment variable."""
    monkeypatch.delenv("HEX_API_KEY", raising=False)


@pytest.fixture
def mock_hex_client():
    """Mock the HexClient instance.

    Yields:
        Mock: Mocked HexClient instance.

    """
    with patch("hex_toolkit.cli.get_client") as mock_get_client:
        client = Mock()
        mock_get_client.return_value = client
        yield client


@pytest.fixture
def sample_project():
    """Create a sample project for testing.

    Returns:
        Project: A sample Project instance with test data.

    """
    return Project(
        id=UUID("12345678-1234-1234-1234-123456789012"),
        title="Test Project",
        description="A test project for CLI testing",
        type=ProjectType.PROJECT,
        creator=CreatorInfo(email="creator@test.com"),
        owner=UserInfo(email="owner@test.com"),
        status=StatusInfo(name="Published"),
        createdAt=datetime(2024, 1, 1, 0, 0, 0),
        lastEditedAt=datetime(2024, 1, 2, 0, 0, 0),
        lastPublishedAt=datetime(2024, 1, 3, 0, 0, 0),
        archivedAt=None,
        trashedAt=None,
        categories=[CategoryInfo(name="Test", description="Test category")],
        reviews=ReviewsInfo(required=False),
        analytics=AnalyticsInfo(
            lastViewedAt=datetime(2024, 1, 4, 0, 0, 0),
            publishedResultsUpdatedAt=datetime(2024, 1, 3, 0, 0, 0),
            appViews=AppViewsInfo(
                allTime=1000,
                lastThirtyDays=100,
                lastFourteenDays=50,
                lastSevenDays=25,
            ),
        ),
        schedules=[],
        sharing=SharingInfo(
            workspace=WorkspaceAccess(access=AccessLevel.CAN_VIEW),
            publicWeb=PublicWebAccess(access=AccessLevel.NONE),
            support=SupportAccess(access=AccessLevel.NONE),
            users=[],
            groups=[],
            collections=[],
        ),
    )


@pytest.fixture
def sample_projects(sample_project):  # noqa: ARG001
    """Create a list of sample projects.

    Returns:
        list[Project]: A list of sample Project instances.

    """
    import uuid

    projects = []
    for i in range(3):
        project = Project(
            id=uuid.uuid4(),
            title=f"Project {i}",
            description=f"Description for project {i}",
            type=ProjectType.PROJECT,
            creator=CreatorInfo(email=f"creator{i}@test.com"),
            owner=UserInfo(email=f"owner{i}@test.com"),
            status=StatusInfo(name="Published" if i % 2 == 0 else "Draft"),
            createdAt=datetime(2024, 1, i + 1, 0, 0, 0),
            lastEditedAt=datetime(2024, 1, i + 2, 0, 0, 0),
            lastPublishedAt=datetime(2024, 1, i + 2, 0, 0, 0) if i % 2 == 0 else None,
            archivedAt=None,
            trashedAt=None,
            reviews=ReviewsInfo(required=False),
            analytics=AnalyticsInfo(
                lastViewedAt=datetime(2024, 1, i + 3, 0, 0, 0),
                publishedResultsUpdatedAt=datetime(2024, 1, i + 2, 0, 0, 0),
                appViews=AppViewsInfo(
                    allTime=100 * (i + 1),
                    lastThirtyDays=10 * (i + 1),
                    lastFourteenDays=5 * (i + 1),
                    lastSevenDays=2 * (i + 1),
                ),
            ),
        )
        projects.append(project)
    return projects


@pytest.fixture
def sample_run_info():
    """Create sample run info for testing.

    Returns:
        Mock: A mock object with run information.

    """
    return Mock(
        run_id="87654321-4321-4321-4321-210987654321",
        project_id="12345678-1234-1234-1234-123456789012",
        run_url="https://test.hex.tech/app/runs/test-run",
        run_status_url="https://test.hex.tech/api/v1/projects/test/runs/test-run",
    )


@pytest.fixture
def sample_run_status():
    """Create sample run status for testing.

    Returns:
        Mock: A mock object with run status information.

    """
    return Mock(
        run_id="87654321-4321-4321-4321-210987654321",
        project_id="12345678-1234-1234-1234-123456789012",
        status="COMPLETED",
        start_time=datetime(2024, 1, 1, 10, 0, 0),
        end_time=datetime(2024, 1, 1, 10, 5, 0),
    )


@pytest.fixture
def sample_runs():
    """Create sample runs for testing.

    Returns:
        list[Mock]: A list of mock run objects with varying statuses.

    """
    runs = []
    statuses = ["COMPLETED", "RUNNING", "FAILED", "PENDING"]
    for i in range(4):
        run = Mock(
            run_id=f"run-{i}",
            project_id="test-project",
            status=statuses[i],
            start_time=datetime(2024, 1, 1, 10, i, 0),
            end_time=datetime(2024, 1, 1, 10, i + 5, 0) if i < 2 else None,
        )
        runs.append(run)
    return runs


@pytest.fixture
def mock_list_response(sample_projects):
    """Create a mock list response.

    Returns:
        Mock: A mock ProjectList response object.

    """
    return Mock(
        values=sample_projects,
        pagination=Mock(after=None),
    )


@pytest.fixture
def mock_console():
    """Mock the Rich console to avoid output during tests.

    Yields:
        Mock: Mocked Rich console object.

    """
    with patch("hex_toolkit.cli.console") as mock:
        yield mock


@pytest.fixture
def mock_progress():
    """Mock Rich Progress to avoid output during tests.

    Yields:
        Mock: Mocked Rich Progress class.

    """
    with patch("hex_toolkit.cli.Progress") as mock:
        yield mock
